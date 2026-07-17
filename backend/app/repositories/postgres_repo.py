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
        error_message: str | None = None,
        entities_extracted: int | None = None
    ) -> Upload | None:
        async with get_db_session() as db:
            values = {"status": status}
            if pipeline_stage is not None:
                values["pipeline_stage"] = pipeline_stage
            if error_message is not None:
                values["error_message"] = error_message
            if entities_extracted is not None:
                values["entities_extracted"] = entities_extracted
                
            result = await db.execute(
                update(Upload)
                .where(Upload.job_id == job_id)
                .values(**values)
                .returning(Upload)
            )
            await db.commit()
            return result.scalar_one_or_none()

    @staticmethod
    async def log_chat_message(query: str, answer: str, confidence: float) -> None:
        """Log a chat query and response to the database."""
        async with get_db_session() as db:
            from sqlalchemy import text
            await db.execute(
                text("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id SERIAL PRIMARY KEY,
                    query TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    confidence FLOAT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
            )
            await db.execute(
                text("INSERT INTO chat_messages (query, answer, confidence) VALUES (:q, :a, :c)"),
                {"q": query, "a": answer, "c": confidence}
            )
            await db.commit()

    @staticmethod
    async def log_agent_run(agent_type: str, target_id: str | None, status: str, result: str) -> None:
        """Log an agent execution."""
        async with get_db_session() as db:
            from sqlalchemy import text
            await db.execute(
                text("""
                CREATE TABLE IF NOT EXISTS agent_logs (
                    id SERIAL PRIMARY KEY,
                    agent_type TEXT NOT NULL,
                    target_id TEXT,
                    status TEXT NOT NULL,
                    result TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
            )
            await db.execute(
                text("INSERT INTO agent_logs (agent_type, target_id, status, result) VALUES (:a, :t, :s, :r)"),
                {"a": agent_type, "t": target_id, "s": status, "r": result}
            )
            await db.commit()

    @staticmethod
    async def log_evaluation(query: str, latency: float, score: float, details: str) -> None:
        """Log an evaluation benchmark result."""
        async with get_db_session() as db:
            from sqlalchemy import text
            await db.execute(
                text("""
                CREATE TABLE IF NOT EXISTS evaluation_results (
                    id SERIAL PRIMARY KEY,
                    query TEXT NOT NULL,
                    latency_sec FLOAT NOT NULL,
                    score FLOAT NOT NULL,
                    details TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
            )
            await db.execute(
                text("INSERT INTO evaluation_results (query, latency_sec, score, details) VALUES (:q, :l, :s, :d)"),
                {"q": query, "l": latency, "s": score, "d": details}
            )
            await db.commit()

    @staticmethod
    async def log_compliance_review(flag_hash: str, status: str) -> None:
        """Log a human review of a compliance flag."""
        async with get_db_session() as db:
            from sqlalchemy import text
            await db.execute(
                text("""
                CREATE TABLE IF NOT EXISTS compliance_reviews (
                    flag_hash TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
            )
            await db.execute(
                text("""
                INSERT INTO compliance_reviews (flag_hash, status) 
                VALUES (:f, :s) 
                ON CONFLICT (flag_hash) DO UPDATE SET status = :s
                """),
                {"f": flag_hash, "s": status}
            )
            await db.commit()

    @staticmethod
    async def get_dismissed_flags() -> list[str]:
        """Get a list of flag hashes that have been dismissed."""
        async with get_db_session() as db:
            from sqlalchemy import text
            try:
                result = await db.execute(
                    text("SELECT flag_hash FROM compliance_reviews WHERE status = 'dismissed'")
                )
                return [row[0] for row in result.fetchall()]
            except Exception:
                # Table might not exist yet
                return []

postgres_repo = PostgresRepo()
