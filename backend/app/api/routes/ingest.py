"""
api/routes/ingest.py
────────────────────
POST /ingest endpoint for document upload.
"""
import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, UploadFile

from app.infrastructure.logger import log
from app.pipeline.ingestion_pipeline import run_ingestion
from app.repositories.postgres_repo import postgres_repo
from app.shared.api_models import IngestResponse
from app.shared.ontology import DocType

router = APIRouter(tags=["Ingestion"])

@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
) -> IngestResponse:
    """Upload a document and trigger the ingestion pipeline."""
    job_id = f"job-{uuid.uuid4().hex[:8]}"
    doc_id = f"doc-{uuid.uuid4().hex[:8]}"
    
    # Infer doc_type from filename if possible, defaulting to MAINTENANCE_LOG
    doc_type = DocType.MAINTENANCE_LOG

    log.info("ingest.request_received", filename=file.filename, job_id=job_id)

    # Save uploaded file to temp path
    tmp_path = Path(tempfile.gettempdir()) / f"{job_id}_{file.filename}"
    with open(tmp_path, "wb") as f:
        f.write(await file.read())

    # Create tracking record
    await postgres_repo.create_upload(
        job_id=job_id,
        doc_id=doc_id,
        filename=file.filename or "unknown",
        doc_type=doc_type.value
    )

    # Trigger background pipeline
    background_tasks.add_task(run_ingestion, job_id, tmp_path)

    return IngestResponse(
        job_id=job_id,
        doc_id=doc_id,
        filename=file.filename or "unknown",
        doc_type=doc_type,
        status="queued",
        message="Document queued for processing."
    )
