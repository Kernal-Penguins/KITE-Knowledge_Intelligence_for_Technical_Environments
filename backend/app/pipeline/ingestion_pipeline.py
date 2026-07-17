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
        
        # Fetch the upload record to get doc_id
        upload = await postgres_repo.get_upload_by_job_id(job_id)
        if not upload:
            raise ValueError(f"Upload record not found for job_id: {job_id}")
            
        doc_id = upload.doc_id

        # Run sync parsing in threadpool
        parsed_md = await asyncio.to_thread(parser_service.parse_document, file_path)
        
        # Step 2: Extract Entities
        await postgres_repo.update_upload_status(job_id, status="extracting", pipeline_stage="extract")
        from app.services.ingestion.extraction_service import extraction_service
        
        extraction_result = await extraction_service.run_extraction(text=parsed_md, doc_id=doc_id)
        
        # Day 3: Mark complete and save counts
        total_entities = (
            len(extraction_result.equipment) + 
            len(extraction_result.failures) + 
            len(extraction_result.procedures) + 
            len(extraction_result.personnel) + 
            len(extraction_result.regulations) + 
            len(extraction_result.inspections) + 
            len(extraction_result.work_orders) + 
            len(extraction_result.incidents) + 
            len(extraction_result.relationships)
        )
        
        # We need a new method in postgres_repo or a direct update to set entities_extracted.
        # Let's update postgres_repo as well.
        await postgres_repo.update_upload_status(
            job_id, 
            status="complete", 
            pipeline_stage="extract",
            entities_extracted=total_entities
        )
        
        log.info("pipeline.ingestion.completed", job_id=job_id, entities_extracted=total_entities)

    except Exception as exc:
        log.error("pipeline.ingestion.failed", job_id=job_id, error=str(exc))
        await postgres_repo.update_upload_status(job_id, status="failed", error_message=str(exc))
        raise
