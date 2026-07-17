"""
pipeline/ingestion_pipeline.py
──────────────────────────────
Orchestrates the steps for document ingestion:
1. Parse
2. Extract
3. Resolve & Merge
4. Write to Graph
5. Vectorize & Upsert (Day 5)
"""
import asyncio
import uuid
from pathlib import Path

from qdrant_client.http.models import PointStruct

from app.infrastructure.logger import log
from app.repositories.postgres_repo import postgres_repo
from app.services.ingestion.parser_service import parser_service


async def run_ingestion(job_id: str, file_path: Path):
    """Run the ingestion pipeline on a document."""
    log.info("pipeline.ingestion.started", job_id=job_id)
    try:
        # Step 1: Parse
        await postgres_repo.update_upload_status(job_id, status="parsing", pipeline_stage="parse")
        
        upload = await postgres_repo.get_upload_by_job_id(job_id)
        if not upload:
            raise ValueError(f"Upload record not found for job_id: {job_id}")
            
        doc_id = upload.doc_id

        parsed_md = await asyncio.to_thread(parser_service.parse_document, file_path)
        
        # Step 2: Extract Entities
        await postgres_repo.update_upload_status(job_id, status="extracting", pipeline_stage="extract")
        from app.services.ingestion.extraction_service import extraction_service
        
        extraction_result = await extraction_service.run_extraction(text=parsed_md, doc_id=doc_id)
        
        # Step 3: Resolve & Merge
        await postgres_repo.update_upload_status(job_id, status="resolving", pipeline_stage="resolve")
        from app.services.ingestion.resolution_service import resolution_service
        
        resolved_result = await resolution_service.resolve_entities(extraction_result)
        
        total_entities = (
            len(extraction_result.equipment) + len(extraction_result.failures) + 
            len(extraction_result.procedures) + len(extraction_result.personnel) + 
            len(extraction_result.regulations) + len(extraction_result.inspections) + 
            len(extraction_result.work_orders) + len(extraction_result.incidents) + 
            len(extraction_result.relationships)
        )

        total_nodes = (
            len(resolved_result.equipment) + len(resolved_result.failures) + 
            len(resolved_result.procedures) + len(resolved_result.personnel) + 
            len(resolved_result.regulations) + len(resolved_result.inspections) + 
            len(resolved_result.work_orders) + len(resolved_result.incidents)
        )
        
        # Step 4: Write to Graph
        await postgres_repo.update_upload_status(job_id, status="writing_graph", pipeline_stage="graph")
        from app.repositories.neo4j_repo import neo4j_repo
        
        await neo4j_repo.write_extraction_result(resolved_result)
        
        # Step 5: Vectorize & Upsert (Day 5)
        await postgres_repo.update_upload_status(job_id, status="vectorizing", pipeline_stage="vectorize")
        from app.infrastructure.embedder import embedder
        from app.repositories.qdrant_repo import qdrant_repo

        # Simple overlap chunker (approx 500 words ~ 2500 chars, 250 char overlap)
        chunk_size = 2500
        overlap = 250
        chunks = []
        start = 0
        while start < len(parsed_md):
            end = start + chunk_size
            chunks.append(parsed_md[start:end])
            if end >= len(parsed_md):
                break
            start = end - overlap

        # Embed chunks
        vectors = await asyncio.to_thread(embedder.embed_batch, chunks)
        
        # Collect all node IDs from the resolved result to map to chunks
        all_node_ids = []
        for eq in resolved_result.equipment: all_node_ids.append(eq.tag_id)
        for f in resolved_result.failures: all_node_ids.append(f.failure_id)
        for p in resolved_result.procedures: all_node_ids.append(p.procedure_id)
        for p in resolved_result.personnel: all_node_ids.append(p.person_id)
        for r in resolved_result.regulations: all_node_ids.append(r.reg_id)
        for i in resolved_result.inspections: all_node_ids.append(i.inspection_id)
        for w in resolved_result.work_orders: all_node_ids.append(w.wo_id)
        for i in resolved_result.incidents: all_node_ids.append(i.incident_id)

        points = []
        for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
            # Match node ids present in this chunk
            chunk_nodes = [node_id for node_id in all_node_ids if node_id.lower() in chunk.lower()]
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={
                        "text": chunk,
                        "doc_id": doc_id,
                        "graph_node_ids": chunk_nodes
                    }
                )
            )

        if points:
            await qdrant_repo.upsert_chunks(points)

        await postgres_repo.update_upload_status(
            job_id, 
            status="complete", 
            pipeline_stage="complete",
            entities_extracted=total_entities
        )
        
        log.info("pipeline.ingestion.completed", job_id=job_id, entities=total_entities, nodes=total_nodes, chunks=len(points))

    except Exception as exc:
        log.error("pipeline.ingestion.failed", job_id=job_id, error=str(exc))
        await postgres_repo.update_upload_status(job_id, status="failed", error_message=str(exc))
        raise
