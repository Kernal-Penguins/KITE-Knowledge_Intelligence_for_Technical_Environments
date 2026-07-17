"""
pipeline/ingestion_pipeline.py
──────────────────────────────
Orchestrates the steps for document ingestion:
1. Parse
2. Extract (Day 3)
3. Resolve & Merge (Day 4)
4. Embed & Vectorize (Day 5)
"""
import asyncio
from pathlib import Path

from app.infrastructure.logger import log
from app.repositories.postgres_repo import postgres_repo
from app.services.ingestion.parser_service import parser_service


async def run_ingestion(job_id: str, file_path: Path):
    """Run the ingestion pipeline on a document."""
    log.info("pipeline.ingestion.started", job_id=job_id)
    try:
        # Step 1: Parse
        await postgres_repo.update_upload_status(job_id, status="parsing", pipeline_stage="parse")
        
        # Run sync parsing in threadpool
        parsed_md = await asyncio.to_thread(parser_service.parse_document, file_path)
        
        # Day 2: We just mark as complete for now.
        await postgres_repo.update_upload_status(job_id, status="complete", pipeline_stage="parse")
        log.info("pipeline.ingestion.completed", job_id=job_id)

    except Exception as exc:
        log.error("pipeline.ingestion.failed", job_id=job_id, error=str(exc))
        await postgres_repo.update_upload_status(job_id, status="failed", error_message=str(exc))
        raise
