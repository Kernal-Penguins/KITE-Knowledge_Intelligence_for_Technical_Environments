"""
api/routes/agents.py
────────────────────
Endpoints for Agentic operations: RCA, Compliance, Lessons-Learned.
"""
import json

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, field_validator

from app.infrastructure.logger import log
from app.repositories.postgres_repo import postgres_repo
from app.services.agents.compliance_service import compliance_service
from app.services.agents.lessons_service import lessons_service
from app.services.agents.rca_service import rca_service

router = APIRouter(prefix="/agents", tags=["Agents"])

_VALID_REVIEW_STATUSES = {"dismissed", "confirmed", "pending"}


class ReviewRequest(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in _VALID_REVIEW_STATUSES:
            raise ValueError(f"status must be one of: {sorted(_VALID_REVIEW_STATUSES)}")
        return v


# ── RCA ─────────────────────────────────────────────────────────────────────


@router.get("/rca/{equipment_id}")
async def run_rca(equipment_id: str):
    """Run a Root Cause Analysis for a given equipment tag ID."""
    stripped_id = equipment_id.strip()
    if not stripped_id:
        raise HTTPException(status_code=422, detail="equipment_id must not be blank.")

    try:
        result = await rca_service.generate_rca(stripped_id)
    except Exception as exc:
        log.error("agents.rca.failed", equipment_id=stripped_id, error=str(exc))
        # Best-effort log to Postgres
        try:
            await postgres_repo.log_agent_run("rca", stripped_id, "failed", str(exc))
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(exc))

    try:
        await postgres_repo.log_agent_run(
            agent_type="rca",
            target_id=stripped_id,
            status="success",
            result=json.dumps(result),
        )
    except Exception as log_exc:
        log.warning("agents.rca.log_failed", error=str(log_exc))

    return result


# ── Lessons-Learned ──────────────────────────────────────────────────────────


@router.post("/lessons/cluster")
async def run_lessons_clustering(
    threshold: float = Query(default=0.85, ge=0.0, le=1.0, description="Cosine similarity threshold for failure clustering (0.0–1.0)."),
):
    """Cluster failure descriptions and write SIMILAR_FAILURE_MODE edges to the graph."""

    try:
        result = await lessons_service.cluster_failures(similarity_threshold=threshold)
    except Exception as exc:
        log.error("agents.lessons.failed", error=str(exc))
        try:
            await postgres_repo.log_agent_run("lessons", None, "failed", str(exc))
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(exc))

    try:
        await postgres_repo.log_agent_run(
            agent_type="lessons",
            target_id=None,
            status="success",
            result=json.dumps(result),
        )
    except Exception as log_exc:
        log.warning("agents.lessons.log_failed", error=str(log_exc))

    return result


# ── Compliance ───────────────────────────────────────────────────────────────


@router.get("/compliance")
async def run_compliance_audit():
    """Run the scoped compliance audit (5 Cypher rules) against the knowledge graph."""
    try:
        result = await compliance_service.run_audit()
    except Exception as exc:
        log.error("agents.compliance.failed", error=str(exc))
        try:
            await postgres_repo.log_agent_run("compliance", None, "failed", str(exc))
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(exc))

    try:
        await postgres_repo.log_agent_run(
            agent_type="compliance",
            target_id=None,
            status=result.get("status", "unknown"),
            result=json.dumps(result),
        )
    except Exception as log_exc:
        log.warning("agents.compliance.log_failed", error=str(log_exc))

    return result


@router.post("/compliance/flags/{flag_hash}/review")
async def review_compliance_flag(flag_hash: str, req: ReviewRequest):
    """Record a human review decision on a compliance gap flag."""
    try:
        await postgres_repo.log_compliance_review(flag_hash, req.status)
        return {"status": "success", "flag_hash": flag_hash, "new_status": req.status}
    except Exception as exc:
        log.error("agents.compliance.review_failed", flag_hash=flag_hash, error=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))
