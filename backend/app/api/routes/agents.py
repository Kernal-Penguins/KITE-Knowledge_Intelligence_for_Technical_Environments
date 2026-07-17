"""
api/routes/agents.py
────────────────────
Endpoints for Agentic operations.
"""
import json

from fastapi import APIRouter, HTTPException

from app.repositories.postgres_repo import postgres_repo
from app.services.agents.compliance_service import compliance_service
from app.services.agents.lessons_service import lessons_service
from app.services.agents.rca_service import rca_service

router = APIRouter(prefix="/agents", tags=["Agents"])

@router.get("/rca/{equipment_id}")
async def run_rca(equipment_id: str):
    try:
        result = await rca_service.generate_rca(equipment_id)
        
        await postgres_repo.log_agent_run(
            agent_type="rca",
            target_id=equipment_id,
            status="success",
            result=json.dumps(result)
        )
        return result
    except Exception as e:
        await postgres_repo.log_agent_run("rca", equipment_id, "failed", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/lessons/cluster")
async def run_lessons_clustering(threshold: float = 0.85):
    try:
        result = await lessons_service.cluster_failures(similarity_threshold=threshold)
        
        await postgres_repo.log_agent_run(
            agent_type="lessons",
            target_id=None,
            status="success",
            result=json.dumps(result)
        )
        return result
    except Exception as e:
        await postgres_repo.log_agent_run("lessons", None, "failed", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compliance")
async def run_compliance_audit():
    try:
        result = await compliance_service.run_audit()
        
        await postgres_repo.log_agent_run(
            agent_type="compliance",
            target_id=None,
            status=result["status"],
            result=json.dumps(result)
        )
        return result
    except Exception as e:
        await postgres_repo.log_agent_run("compliance", None, "failed", str(e))
        raise HTTPException(status_code=500, detail=str(e))

from pydantic import BaseModel
class ReviewRequest(BaseModel):
    status: str

@router.post("/compliance/flags/{flag_hash}/review")
async def review_compliance_flag(flag_hash: str, req: ReviewRequest):
    if req.status not in ["dismissed", "confirmed", "pending"]:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    try:
        await postgres_repo.log_compliance_review(flag_hash, req.status)
        return {"status": "success", "flag_hash": flag_hash, "new_status": req.status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
