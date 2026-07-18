"""
api/routes/ingest.py
────────────────────
POST /ingest endpoint for document upload.
"""
import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from app.infrastructure.logger import log
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
