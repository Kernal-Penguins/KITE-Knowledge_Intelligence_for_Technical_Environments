"""
app/main.py
───────────
FastAPI application factory with lifespan management.
Registers all routers and middleware.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.infrastructure.logger import log
from app.infrastructure.neo4j_client import neo4j_client
from app.infrastructure.qdrant_client import qdrant_client
from app.infrastructure.postgres_client import init_db, close_db

# Routers
from app.api.routes.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan handler.
    Startup: connect all databases, create PG tables.
    Shutdown: gracefully close all connections.
    """
    log.info("kite.startup", version=settings.APP_VERSION, env=settings.APP_ENV)

    # Startup
    await init_db()
    await neo4j_client.connect()
    await qdrant_client.connect()

    log.info("kite.ready")

    yield  # Application runs here

    # Shutdown
    log.info("kite.shutdown")
    await neo4j_client.close()
    await qdrant_client.close()
    await close_db()
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
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
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
    app.include_router(health_router)

    # Day 2+ routers (added as built):
    # from app.api.routes.ingest import router as ingest_router
    # from app.api.routes.query import router as query_router
    # from app.api.routes.graph import router as graph_router
    # from app.api.routes.agents.rca import router as rca_router
    # from app.api.routes.agents.compliance import router as compliance_router
    # from app.api.routes.agents.lessons import router as lessons_router
    # app.include_router(ingest_router, prefix="/api/v1")
    # app.include_router(query_router,  prefix="/api/v1")
    # app.include_router(graph_router,  prefix="/api/v1")
    # app.include_router(rca_router,    prefix="/api/v1/agents")
    # app.include_router(compliance_router, prefix="/api/v1/agents")
    # app.include_router(lessons_router,    prefix="/api/v1/agents")

    return app


app = create_app()
