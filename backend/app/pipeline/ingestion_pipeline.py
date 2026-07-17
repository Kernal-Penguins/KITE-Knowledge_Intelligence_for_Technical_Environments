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
        
        # Step 3: Resolve & Merge
        await postgres_repo.update_upload_status(job_id, status="resolving", pipeline_stage="resolve")
        from app.services.ingestion.resolution_service import resolution_service
        
        resolved_result = await resolution_service.resolve_entities(extraction_result)
        
        # Day 3: Total Entities
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

        # Calculate nodes after resolution
        total_nodes = (
            len(resolved_result.equipment) + 
            len(resolved_result.failures) + 
            len(resolved_result.procedures) + 
            len(resolved_result.personnel) + 
            len(resolved_result.regulations) + 
            len(resolved_result.inspections) + 
            len(resolved_result.work_orders) + 
            len(resolved_result.incidents)
        )
            len(resolved_result.equipment) + 
            len(resolved_result.failures) + 
            len(resolved_result.procedures) + 
            len(resolved_result.personnel) + 
            len(resolved_result.regulations) + 
            len(resolved_result.inspections) + 
            len(resolved_result.work_orders) + 
            len(resolved_result.incidents)
        )
        
        # Step 4: Write to Graph
        await postgres_repo.update_upload_status(job_id, status="writing_graph", pipeline_stage="graph")
        from app.repositories.neo4j_repo import neo4j_repo
        
        await neo4j_repo.write_extraction_result(resolved_result)
        
        # We need a new method in postgres_repo or a direct update to set entities_extracted.
        # Let's update postgres_repo as well.
        await postgres_repo.update_upload_status(
            job_id, 
            status="complete", 
            pipeline_stage="graph",
            entities_extracted=total_entities
        )
        
        # Update nodes_created if we want to trace it. (Requires update to postgres_repo but we can skip for brevity if it's not strictly necessary, or update it now).
        # We will just mark complete for Day 4!
        
        log.info("pipeline.ingestion.completed", job_id=job_id, entities_extracted=total_entities, nodes_created=total_nodes)

    except Exception as exc:
        log.error("pipeline.ingestion.failed", job_id=job_id, error=str(exc))
        await postgres_repo.update_upload_status(job_id, status="failed", error_message=str(exc))
        raise
