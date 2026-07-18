"""
scripts/feed_data.py
────────────────────
Batch ingests synthetic document data from Data_feed/synthetic_maintenance_docs/
into KITE (Postgres, Neo4j, Qdrant).
"""
import asyncio
import shutil
import sys
import tempfile
import uuid
from pathlib import Path

# Add backend directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.infrastructure.logger import log
from app.infrastructure.neo4j_client import neo4j_client
from app.infrastructure.postgres_client import init_db
from app.infrastructure.qdrant_client import qdrant_client
from app.pipeline.ingestion_pipeline import run_ingestion
from app.repositories.postgres_repo import postgres_repo
from app.shared.ingest_utils import infer_doc_type

DATA_FEED_DIR = Path(__file__).resolve().parent.parent.parent / "Data_feed" / "synthetic_maintenance_docs"

# Held-back set per MANIFEST.md (for demonstrating dynamic graph updates)
HELD_BACK_FILES = {
    "ML-CV220-2026-06-09.txt",
    "WO-10312.txt",
    "IR-GEN04-2026-06.txt",
    "ML-CB15-2026-05-14.txt",
    "WO-10305.txt",
}


def safe_print(msg: str):
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"), flush=True)


async def feed_documents(include_held_back: bool = True, include_corrupted: bool = True):
    """Feed synthetic documents into the system."""
    log.info("feed_data.started", path=str(DATA_FEED_DIR))

    if not DATA_FEED_DIR.exists():
        safe_print(f"Error: Data feed directory not found at {DATA_FEED_DIR}")
        return

    # Ensure infrastructure connections are initialized
    await init_db()
    await neo4j_client.connect()
    await qdrant_client.connect()

    folders = ["sops", "maintenance_logs", "work_orders", "inspection_reports", "incident_reports"]
    if include_corrupted:
        folders.append("corrupted")

    file_paths: list[Path] = []
    for folder in folders:
        folder_dir = DATA_FEED_DIR / folder
        if folder_dir.exists():
            for p in folder_dir.glob("*"):
                if p.is_file() and not p.name.startswith("."):
                    if not include_held_back and p.name in HELD_BACK_FILES:
                        log.info("feed_data.skipping_held_back", filename=p.name)
                        continue
                    file_paths.append(p)

    safe_print(f"Found {len(file_paths)} documents to ingest.")
    success_count = 0
    fail_count = 0

    for i, file_path in enumerate(file_paths, 1):
        job_id = f"job-feed-{uuid.uuid4().hex[:8]}"
        doc_id = f"doc-feed-{uuid.uuid4().hex[:8]}"
        doc_type = infer_doc_type(file_path.name)

        rel_path = file_path.relative_to(DATA_FEED_DIR)
        safe_print(f"[{i}/{len(file_paths)}] Ingesting {rel_path} ({doc_type.value})...")

        # Copy to temp file so source dataset is preserved
        tmp_path = Path(tempfile.gettempdir()) / f"{job_id}_{file_path.name}"
        shutil.copy(file_path, tmp_path)

        # Create upload tracking record in Postgres
        await postgres_repo.create_upload(
            job_id=job_id,
            doc_id=doc_id,
            filename=file_path.name,
            doc_type=doc_type.value,
        )

        # Run pipeline on temp file
        try:
            await run_ingestion(job_id, tmp_path)
            upload = await postgres_repo.get_upload_by_job_id(job_id)
            if upload and upload.status == "complete":
                success_count += 1
                safe_print(f"  -> SUCCESS ({upload.entities_extracted or 0} entities)")
            else:
                fail_count += 1
                err = upload.error_message if upload else "Unknown status"
                safe_print(f"  -> HANDLED ERROR/CORRUPT: {err}")
        except Exception as e:
            fail_count += 1
            safe_print(f"  -> ERROR: {str(e)}")

        # Pace requests to respect Gemini Free Tier rate limits
        await asyncio.sleep(6.0)

    safe_print("\n" + "=" * 50)
    safe_print(f"Ingestion Complete! Total: {len(file_paths)} | Success: {success_count} | Handled Failures/Corrupted: {fail_count}")
    safe_print("=" * 50)


if __name__ == "__main__":
    asyncio.run(feed_documents(include_held_back=True, include_corrupted=True))
