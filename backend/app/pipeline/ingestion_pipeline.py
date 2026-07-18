"""
pipeline/ingestion_pipeline.py
──────────────────────────────
Orchestrates the document ingestion steps:
  1. Parse   → markdown text
  2. Extract → structured entities via LLM
  3. Resolve → merge duplicate entity references
  4. Graph   → write to Neo4j
  5. Vectorize → chunk, embed, upsert to Qdrant

The temp file is always cleaned up at the end, whether the pipeline
succeeds or fails.
"""
import asyncio
import uuid
from pathlib import Path

from qdrant_client.http.models import PointStruct

from app.infrastructure.logger import log
from app.repositories.postgres_repo import postgres_repo
from app.services.ingestion.parser_service import parser_service


async def run_ingestion(job_id: str, file_path: Path) -> None:
    """
    Run the full ingestion pipeline on a document.

    This function is intended to run as a FastAPI BackgroundTask.
    It never re-raises exceptions — failures are recorded in Postgres
    so the caller can poll the job status.
    """
    log.info("pipeline.ingestion.started", job_id=job_id, file=str(file_path))
    try:
        # ── Step 0: Validate the upload record exists ──────────────────────
        upload = await postgres_repo.get_upload_by_job_id(job_id)
        if not upload:
            raise ValueError(f"Upload record not found for job_id={job_id!r}")

        doc_id = upload.doc_id

        # ── Step 1: Parse ──────────────────────────────────────────────────
        await postgres_repo.update_upload_status(
            job_id, status="parsing", pipeline_stage="parse"
        )
        parsed_md: str = await asyncio.to_thread(parser_service.parse_document, file_path)

        if not parsed_md.strip():
            raise ValueError(
                "Docling returned empty text for the document. "
                "The file may be corrupt, image-only (non-OCR'd), or entirely blank."
            )

        # ── Step 2: Extract Entities ───────────────────────────────────────
        await postgres_repo.update_upload_status(
            job_id, status="extracting", pipeline_stage="extract"
        )
        from app.services.ingestion.extraction_service import extraction_service

        extraction_result = await extraction_service.run_extraction(
            text=parsed_md, doc_id=doc_id
        )

        # ── Step 3: Resolve & Merge ────────────────────────────────────────
        await postgres_repo.update_upload_status(
            job_id, status="resolving", pipeline_stage="resolve"
        )
        from app.services.ingestion.resolution_service import resolution_service

        resolved_result = await resolution_service.resolve_entities(extraction_result)

        total_entities = (
            len(extraction_result.equipment)
            + len(extraction_result.failures)
            + len(extraction_result.procedures)
            + len(extraction_result.personnel)
            + len(extraction_result.regulations)
            + len(extraction_result.inspections)
            + len(extraction_result.work_orders)
            + len(extraction_result.incidents)
            + len(extraction_result.relationships)
        )

        total_nodes = (
            len(resolved_result.equipment)
            + len(resolved_result.failures)
            + len(resolved_result.procedures)
            + len(resolved_result.personnel)
            + len(resolved_result.regulations)
            + len(resolved_result.inspections)
            + len(resolved_result.work_orders)
            + len(resolved_result.incidents)
        )

        # ── Step 4: Write to Graph ─────────────────────────────────────────
        await postgres_repo.update_upload_status(
            job_id, status="writing_graph", pipeline_stage="graph"
        )
        from app.repositories.neo4j_repo import neo4j_repo

        await neo4j_repo.write_extraction_result(resolved_result)

        # ── Step 5: Chunk, Embed & Upsert ─────────────────────────────────
        await postgres_repo.update_upload_status(
            job_id, status="vectorizing", pipeline_stage="vectorize"
        )
        from app.infrastructure.embedder import embedder
        from app.repositories.qdrant_repo import qdrant_repo

        # Overlap-aware character chunker (~500 words ≈ 2 500 chars, 250-char overlap)
        CHUNK_SIZE = 2_500
        OVERLAP = 250
        chunks: list[str] = []
        start = 0
        while start < len(parsed_md):
            end = start + CHUNK_SIZE
            chunks.append(parsed_md[start:end])
            if end >= len(parsed_md):
                break
            start = end - OVERLAP

        if chunks:
            vectors = await asyncio.to_thread(embedder.embed_batch, chunks)

            # Collect canonical node IDs for payload linking
            all_node_ids: list[str] = []
            for eq in resolved_result.equipment:
                all_node_ids.append(eq.tag_id)
            for f in resolved_result.failures:
                all_node_ids.append(f.failure_id)
            for p in resolved_result.procedures:
                all_node_ids.append(p.procedure_id)
            for p in resolved_result.personnel:
                all_node_ids.append(p.person_id)
            for r in resolved_result.regulations:
                all_node_ids.append(r.reg_id)
            for i in resolved_result.inspections:
                all_node_ids.append(i.inspection_id)
            for w in resolved_result.work_orders:
                all_node_ids.append(w.wo_id)
            for i in resolved_result.incidents:
                all_node_ids.append(i.incident_id)

            points: list[PointStruct] = []
            for chunk, vector in zip(chunks, vectors):
                chunk_lower = chunk.lower()
                linked_nodes = [nid for nid in all_node_ids if nid.lower() in chunk_lower]
                points.append(
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector=vector,
                        payload={
                            "text": chunk,
                            "doc_id": doc_id,
                            "graph_node_ids": linked_nodes,
                        },
                    )
                )

            await qdrant_repo.upsert_chunks(points)
        else:
            points = []

        await postgres_repo.update_upload_status(
            job_id,
            status="complete",
            pipeline_stage="complete",
            entities_extracted=total_entities,
        )

        log.info(
            "pipeline.ingestion.completed",
            job_id=job_id,
            entities=total_entities,
            nodes=total_nodes,
            chunks=len(points),
        )

    except Exception as exc:
        log.error("pipeline.ingestion.failed", job_id=job_id, error=str(exc), exc_info=True)
        try:
            await postgres_repo.update_upload_status(
                job_id, status="failed", error_message=str(exc)
            )
        except Exception as db_exc:
            # If the status update itself fails, just log — don't crash the background task
            log.error(
                "pipeline.ingestion.status_update_failed",
                job_id=job_id,
                db_error=str(db_exc),
            )
    finally:
        # Always clean up the temp file regardless of success or failure
        try:
            file_path.unlink(missing_ok=True)
            log.info("pipeline.ingestion.tmp_cleaned", job_id=job_id, file=str(file_path))
        except Exception as cleanup_exc:
            log.warning(
                "pipeline.ingestion.tmp_cleanup_failed",
                job_id=job_id,
                error=str(cleanup_exc),
            )
