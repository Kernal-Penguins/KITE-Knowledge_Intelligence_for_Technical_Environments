"""
infrastructure/postgres_client.py
──────────────────────────────────
Async PostgreSQL engine and session factory via SQLAlchemy.

Usage:
    from app.infrastructure.postgres_client import get_db_session
    async with get_db_session() as session:
        ...
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings
from app.db.models import Base
from app.infrastructure.logger import log


_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker | None = None


async def init_db() -> None:
    """Create engine, run create_all(), called on app startup."""
    global _engine, _session_factory

    _engine = create_async_engine(
        settings.DATABASE_URL,
        echo=not settings.is_production,
        pool_size=10,
        max_overflow=20,
    )

    _session_factory = async_sessionmaker(
        bind=_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    log.info("postgres.connected", url=settings.DATABASE_URL.split("@")[-1])


async def close_db() -> None:
    """Dispose engine on app shutdown."""
    global _engine
    if _engine:
        await _engine.dispose()
        log.info("postgres.disconnected")


async def ping_db() -> bool:
    """Health check."""
    try:
        async with _engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        return True
    except Exception as exc:
        log.warning("postgres.ping_failed", error=str(exc))
        return False


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async SQLAlchemy session."""
    if not _session_factory:
        raise RuntimeError("Database not initialised. Call init_db() first.")
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
