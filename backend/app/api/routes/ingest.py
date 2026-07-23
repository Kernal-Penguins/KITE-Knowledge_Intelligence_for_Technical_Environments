"""
api/routes/ingest.py
────────────────────
POST /ingest endpoint for document upload.
"""
import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, Query
from sqlalchemy import text

from app.infrastructure.logger import log
from app.infrastructure.neo4j_client import neo4j_client
from app.infrastructure.postgres_client import get_db_session
from app.pipeline.ingestion_pipeline import run_ingestion
from app.repositories.postgres_repo import postgres_repo
from app.shared.api_models import IngestResponse
from app.shared.ingest_utils import MAX_UPLOAD_BYTES, infer_doc_type
from app.shared.ontology import DocType

router = APIRouter(tags=["Ingestion"])


@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
) -> IngestResponse:
    """Upload a document and trigger the ingestion pipeline."""
    # Sanitise filename — strip path separators to prevent traversal
    raw_name = file.filename or "unknown"
    safe_name = Path(raw_name).name or "unknown"

    job_id = f"job-{uuid.uuid4().hex[:8]}"
    doc_id = f"doc-{uuid.uuid4().hex[:8]}"
    doc_type = infer_doc_type(safe_name)

    log.info("ingest.request_received", filename=safe_name, job_id=job_id)

    # Read body and enforce size limit BEFORE writing to disk
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=422, detail="Uploaded file is empty.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum allowed size is {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.",
        )

    # Write to temp file — guaranteed cleanup via finally
    tmp_path = Path(tempfile.gettempdir()) / f"{job_id}_{safe_name}"
    try:
        tmp_path.write_bytes(content)
    except OSError as exc:
        log.error("ingest.tmp_write_failed", job_id=job_id, error=str(exc))
        raise HTTPException(status_code=500, detail="Failed to buffer uploaded file.")

    # Create tracking record in Postgres — if this fails, clean up the temp file
    try:
        await postgres_repo.create_upload(
            job_id=job_id,
            doc_id=doc_id,
            filename=safe_name,
            doc_type=doc_type.value,
        )
    except Exception as exc:
        tmp_path.unlink(missing_ok=True)
        log.error("ingest.db_record_failed", job_id=job_id, error=str(exc))
        raise HTTPException(status_code=500, detail="Failed to create upload record.")

    # Dispatch background task
    if doc_type == DocType.PID:
        from app.services.ingestion.pid_service import pid_service

        async def run_pid_bg(fp: Path) -> None:
            try:
                await postgres_repo.update_upload_status(job_id, status="extracting_pid")
                await pid_service.process_pid(fp)
                await postgres_repo.update_upload_status(
                    job_id, status="complete", pipeline_stage="pid_extraction"
                )
            except Exception as exc:
                log.error("ingest.pid_bg_failed", job_id=job_id, error=str(exc))
                await postgres_repo.update_upload_status(
                    job_id, status="failed", error_message=str(exc)
                )
            finally:
                fp.unlink(missing_ok=True)

        background_tasks.add_task(run_pid_bg, tmp_path)
    else:
        background_tasks.add_task(run_ingestion, job_id, tmp_path)

    return IngestResponse(
        job_id=job_id,
        doc_id=doc_id,
        filename=safe_name,
        doc_type=doc_type,
        status="queued",
        message="Document queued for processing.",
    )


@router.get("/uploads")
async def list_uploads(
    limit: int = Query(default=50, ge=1, le=200),
    status: str | None = Query(default=None, description="Filter by status: queued | complete | failed"),
) -> list[dict]:
    """
    Return a list of past upload jobs from PostgreSQL.
    Ordered newest-first.
    """
    try:
        async with get_db_session() as db:
            where = "WHERE status = :status" if status else ""
            rows = await db.execute(
                text(
                    f"""
                    SELECT job_id, doc_id, filename, doc_type, status,
                           pipeline_stage, error_message, created_at, completed_at
                    FROM uploads
                    {where}
                    ORDER BY created_at DESC
                    LIMIT :limit
                    """  # noqa: S608
                ),
                {"limit": limit, "status": status} if status else {"limit": limit},
            )
            records = rows.mappings().all()
            return [
                {
                    "job_id": r["job_id"],
                    "doc_id": r["doc_id"],
                    "filename": r["filename"],
                    "doc_type": r["doc_type"],
                    "status": r["status"],
                    "pipeline_stage": r["pipeline_stage"],
                    "error_message": r["error_message"],
                    "created_at": r["created_at"].isoformat() if r["created_at"] else None,
                    "completed_at": r["completed_at"].isoformat() if r["completed_at"] else None,
                }
                for r in records
            ]
    except Exception as exc:
        log.warning("ingest.list_uploads_failed", error=str(exc))
        return []


@router.get("/review-queue")
async def get_review_queue(
    limit: int = Query(default=50, ge=1, le=200),
) -> list[dict]:
    """
    Return entity-resolution candidates awaiting human review.
    Sourced from equipment nodes in Neo4j that have alias tags pending confirmation.
    Returns an empty list gracefully when the graph is empty or Neo4j is unavailable.
    """
    items: list[dict] = []
    try:
        async with neo4j_client.session() as session:
            result = await session.run(
                """
                MATCH (n:Equipment)
                WHERE n.aliases IS NOT NULL AND size(n.aliases) > 0
                UNWIND n.aliases AS alias
                RETURN n.id AS entity_a,
                       alias AS entity_b,
                       'Equipment' AS entity_type,
                       coalesce(n.source_doc_ids[0], 'ingestion') AS source
                LIMIT $limit
                """,
                limit=limit,
            )
            records = await result.data()
            for i, rec in enumerate(records):
                entity_a = str(rec.get("entity_a") or "")
                entity_b = str(rec.get("entity_b") or "")
                if not entity_a or not entity_b:
                    continue
                items.append(
                    {
                        "id": f"rq-{i}-{entity_a}-{entity_b}",
                        "entity_a": entity_a,
                        "entity_b": entity_b,
                        "entity_type": str(rec.get("entity_type") or "Equipment"),
                        "confidence": 0.85,
                        "source": str(rec.get("source") or "ingestion"),
                    }
                )
    except RuntimeError as exc:
        log.warning("ingest.review_queue.driver_not_ready", error=str(exc))
        return []
    except Exception as exc:
        log.warning("ingest.review_queue_failed", error=str(exc))
        return []

    return items
