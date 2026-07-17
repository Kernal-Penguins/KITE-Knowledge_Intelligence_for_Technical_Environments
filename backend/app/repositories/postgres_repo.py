"""
repositories/postgres_repo.py
─────────────────────────────
Data access for PostgreSQL tables.
"""

from sqlalchemy import select, update

from app.db.models import Upload
from app.infrastructure.postgres_client import get_db_session


class PostgresRepo:
    """Repository for PostgreSQL operations."""

    @staticmethod
    async def create_upload(
        job_id: str, doc_id: str, filename: str, doc_type: str
    ) -> Upload:
        async with get_db_session() as db:
            upload = Upload(
                job_id=job_id,
                doc_id=doc_id,
                filename=filename,
                doc_type=doc_type,
                status="queued"
            )
            db.add(upload)
            await db.commit()
            await db.refresh(upload)
            return upload

    @staticmethod
    async def get_upload_by_job_id(job_id: str) -> Upload | None:
        async with get_db_session() as db:
            result = await db.execute(select(Upload).where(Upload.job_id == job_id))
            return result.scalar_one_or_none()

    @staticmethod
    async def update_upload_status(
        job_id: str, 
        status: str, 
        pipeline_stage: str | None = None,
        error_message: str | None = None
    ) -> Upload | None:
        async with get_db_session() as db:
            values = {"status": status}
            if pipeline_stage is not None:
                values["pipeline_stage"] = pipeline_stage
            if error_message is not None:
                values["error_message"] = error_message
                
            result = await db.execute(
                update(Upload)
                .where(Upload.job_id == job_id)
                .values(**values)
                .returning(Upload)
            )
            await db.commit()
            return result.scalar_one_or_none()

postgres_repo = PostgresRepo()
