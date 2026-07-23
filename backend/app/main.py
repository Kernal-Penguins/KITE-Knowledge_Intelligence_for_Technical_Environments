"""
app/main.py
───────────
FastAPI application factory with lifespan management.
Registers all routers and middleware.
"""
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
from app.api.routes.health import router as health_router
from app.config import settings
from app.infrastructure.logger import log
from app.infrastructure.neo4j_client import neo4j_client
from app.infrastructure.postgres_client import close_db, init_db
from app.infrastructure.qdrant_client import qdrant_client


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """
    Application lifespan handler.
    Startup: connect all databases, create PG tables.
    Shutdown: gracefully close all connections.
    """
    log.info("kite.startup", version=settings.APP_VERSION, env=settings.APP_ENV)

    # Startup — each service is connected independently.
    # A failure here degrades the service but does NOT abort startup,
    # so the /health endpoint can still report which services are unreachable.
    try:
        await init_db()
    except Exception as exc:
        log.error("kite.startup.postgres_failed", error=str(exc))

    try:
        await neo4j_client.connect()
    except Exception as exc:
        log.error("kite.startup.neo4j_failed", error=str(exc))

    try:
        await qdrant_client.connect()
    except Exception as exc:
        log.error("kite.startup.qdrant_failed", error=str(exc))

    log.info("kite.ready")

    yield  # Application runs here

    # Shutdown
    log.info("kite.shutdown")
    try:
        await neo4j_client.close()
    except Exception:
        pass
    try:
        await qdrant_client.close()
    except Exception:
        pass
    try:
        await close_db()
    except Exception:
        pass
    log.info("kite.stopped")


def create_app() -> FastAPI:
    app = FastAPI(
        title="KITE — Knowledge Integration & Tracing Engine",
        description=(
            "GraphRAG platform for industrial knowledge intelligence. "
            "Ingests heterogeneous documents, builds a knowledge graph, "
            "and exposes hybrid retrieval + agentic AI capabilities."
        ),
        version=settings.APP_VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── CORS ─────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────────────
    from app.api.routes.ingest import router as ingest_router
    from app.api.routes.query import router as query_router
    from app.api.routes.agents import router as agents_router
    from app.api.routes.graph import router as graph_router

    app.include_router(health_router)
    app.include_router(ingest_router, prefix="/api/v1")
    app.include_router(query_router, prefix="/api/v1")
    app.include_router(agents_router, prefix="/api/v1")
    app.include_router(graph_router, prefix="/api/v1")

    # Compatibility for /api without /v1
    app.include_router(ingest_router, prefix="/api")
    app.include_router(query_router, prefix="/api")
    app.include_router(agents_router, prefix="/api")
    app.include_router(graph_router, prefix="/api")

    return app


app = create_app()
