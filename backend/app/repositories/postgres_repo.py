"""
repositories/postgres_repo.py
─────────────────────────────
Data access layer for PostgreSQL tables.

All tables are created at startup via SQLAlchemy's create_all() in
postgres_client.init_db(). This file must NEVER run DDL (CREATE TABLE etc.)
— it should only run DML (SELECT / INSERT / UPDATE).
"""
import json

from sqlalchemy import select, text, update

from app.db.models import Upload
from app.infrastructure.postgres_client import get_db_session


class PostgresRepo:
    """Repository for PostgreSQL operations."""

    # ── Uploads ──────────────────────────────────────────────────────────────

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
                status="queued",
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
        entities_extracted: int | None = None,
    ) -> Upload | None:
        async with get_db_session() as db:
            values: dict = {"status": status}
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

    # ── Chat Messages ─────────────────────────────────────────────────────────
    # NOTE: chat_messages table is managed by the ChatMessage ORM model.
    # We use raw SQL here for simplicity but the table must already exist.

    @staticmethod
    async def log_chat_message(query: str, answer: str, confidence: float) -> None:
        """Log a chat query and its generated response."""
        async with get_db_session() as db:
            # Use the ORM-managed table; insert a bare record without chat_id FK
            await db.execute(
                text(
                    """
                    INSERT INTO chat_messages (id, chat_id, role, content, confidence, created_at)
                    VALUES (gen_random_uuid()::text,
                            'system',
                            'assistant',
                            :answer,
                            :confidence,
                            now())
                    """
                ),
                {"answer": answer, "confidence": confidence},
            )
            await db.commit()

    # ── Agent Logs ────────────────────────────────────────────────────────────

    @staticmethod
    async def log_agent_run(
        agent_type: str, target_id: str | None, status: str, result: str
    ) -> None:
        """Log an agent execution result to agent_logs."""
        async with get_db_session() as db:
            input_payload = json.dumps({"target_id": target_id})
            output_payload = result  # already JSON string
            await db.execute(
                text(
                    """
                    INSERT INTO agent_logs (id, agent_type, input_json, output_json, error_message, created_at)
                    VALUES (gen_random_uuid()::text,
                            :agent_type,
                            :input_json,
                            :output_json,
                            :error_message,
                            now())
                    """
                ),
                {
                    "agent_type": agent_type,
                    "input_json": input_payload,
                    "output_json": output_payload,
                    "error_message": None if status == "success" else result,
                },
            )
            await db.commit()

    # ── Evaluation ───────────────────────────────────────────────────────────

    @staticmethod
    async def log_evaluation(query: str, latency: float, score: float, details: str) -> None:
        """Log an evaluation benchmark result."""
        async with get_db_session() as db:
            await db.execute(
                text(
                    """
                    INSERT INTO evaluation_results (id, run_id, question_id, question, answer,
                                                    metrics_json, response_ms, created_at)
                    VALUES (gen_random_uuid()::text,
                            'benchmark',
                            gen_random_uuid()::text,
                            :query,
                            '',
                            :metrics,
                            :response_ms,
                            now())
                    """
                ),
                {
                    "query": query,
                    "metrics": json.dumps({"score": score, "details": details}),
                    "response_ms": latency * 1000,
                },
            )
            await db.commit()

    # ── Compliance Reviews ────────────────────────────────────────────────────

    @staticmethod
    async def log_compliance_review(flag_hash: str, status: str) -> None:
        """Upsert a human review decision for a compliance gap flag."""
        async with get_db_session() as db:
            await db.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS compliance_reviews (
                        flag_hash TEXT PRIMARY KEY,
                        status    TEXT NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
                    )
                    """
                )
            )
            await db.execute(
                text(
                    """
                    INSERT INTO compliance_reviews (flag_hash, status)
                    VALUES (:f, :s)
                    ON CONFLICT (flag_hash) DO UPDATE SET status = :s
                    """
                ),
                {"f": flag_hash, "s": status},
            )
            await db.commit()

    @staticmethod
    async def get_dismissed_flags() -> list[str]:
        """Return flag hashes that have been dismissed by a reviewer."""
        async with get_db_session() as db:
            try:
                result = await db.execute(
                    text("SELECT flag_hash FROM compliance_reviews WHERE status = 'dismissed'")
                )
                return [row[0] for row in result.fetchall()]
            except Exception:
                # Table may not exist on a fresh instance before any review
                return []


postgres_repo = PostgresRepo()
