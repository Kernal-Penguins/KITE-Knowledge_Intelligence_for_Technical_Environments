"""
api/routes/health.py
────────────────────
GET /health   — liveness + dependency connectivity
GET /version  — version metadata
GET /metrics  — live system counters
"""
import time
from datetime import UTC, datetime

from fastapi import APIRouter

from app.config import settings
from app.infrastructure.logger import log
from app.infrastructure.neo4j_client import neo4j_client
from app.infrastructure.postgres_client import ping_db
from app.infrastructure.qdrant_client import qdrant_client
from app.shared.api_models import (
    HealthResponse,
    HealthService,
    MetricsResponse,
    VersionResponse,
)

router = APIRouter(tags=["Observability"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """
    Check connectivity to all three databases.
    Returns 200 even when services are degraded — status field indicates issues.
    """
    t0 = time.monotonic()

    neo4j_ok  = await neo4j_client.ping()
    qdrant_ok = await qdrant_client.ping()
    pg_ok     = await ping_db()

    all_ok = neo4j_ok and qdrant_ok and pg_ok

    response = HealthResponse(
        status="ok" if all_ok else "degraded",
        services={
            "neo4j":    HealthService(status="connected"   if neo4j_ok  else "unreachable"),
            "qdrant":   HealthService(status="connected"   if qdrant_ok else "unreachable"),
            "postgres": HealthService(status="connected"   if pg_ok     else "unreachable"),
        },
        timestamp=datetime.now(UTC),
    )

    log.info(
        "health.checked",
        status=response.status,
        neo4j=neo4j_ok,
        qdrant=qdrant_ok,
        postgres=pg_ok,
        latency_ms=round((time.monotonic() - t0) * 1000, 1),
    )
    return response


@router.get("/version", response_model=VersionResponse)
async def version() -> VersionResponse:
    """Return application version and build metadata."""
    return VersionResponse(
        version=settings.APP_VERSION,
        build="dev",  # replaced by CI with git SHA
        environment=settings.APP_ENV,
    )


@router.get("/metrics", response_model=MetricsResponse)
async def metrics() -> MetricsResponse:
    """
    Return live system counters from Neo4j, Qdrant, and PostgreSQL.
    Counts are approximate and computed on each call (no caching at this scale).
    """
    # Neo4j: node + edge counts
    graph_nodes = 0
    graph_edges = 0
    try:
        async with neo4j_client.session() as session:
            node_result = await session.run("MATCH (n) RETURN count(n) AS c")
            node_rec    = await node_result.single()
            graph_nodes = node_rec["c"] if node_rec else 0

            edge_result = await session.run("MATCH ()-[r]->() RETURN count(r) AS c")
            edge_rec    = await edge_result.single()
            graph_edges = edge_rec["c"] if edge_rec else 0
    except Exception as exc:
        log.warning("metrics.neo4j_failed", error=str(exc))

    # Qdrant: vector count
    qdrant_vectors = 0
    try:
        from app.shared.constants import QDRANT_COLLECTION_NAME
        info = await qdrant_client.client.get_collection(QDRANT_COLLECTION_NAME)
        qdrant_vectors = info.vectors_count or 0
    except Exception as exc:
        log.warning("metrics.qdrant_failed", error=str(exc))

    # PostgreSQL: document + query counts
    docs_ingested   = 0
    queries_served  = 0
    avg_ms          = 0.0
    agent_counts    = {"rca": 0, "compliance": 0, "lessons": 0}

    try:
        from sqlalchemy import text

        from app.infrastructure.postgres_client import get_db_session

        async with get_db_session() as db:
            r = await db.execute(
                text("SELECT COUNT(*) FROM uploads WHERE status = 'complete'")
            )
            docs_ingested = r.scalar() or 0

            r = await db.execute(
                text("SELECT COUNT(*) FROM chat_messages WHERE role = 'assistant'")
            )
            queries_served = r.scalar() or 0

            r = await db.execute(
                text("SELECT AVG(response_ms) FROM chat_messages WHERE role = 'assistant'")
            )
            avg_ms = float(r.scalar() or 0.0)

            for agent in ["rca", "compliance", "lessons"]:
                r = await db.execute(
                    text("SELECT COUNT(*) FROM agent_logs WHERE agent_type = :t"),
                    {"t": agent},
                )
                agent_counts[agent] = r.scalar() or 0
    except Exception as exc:
        log.warning("metrics.postgres_failed", error=str(exc))

    return MetricsResponse(
        documents_ingested=docs_ingested,
        graph_nodes=graph_nodes,
        graph_edges=graph_edges,
        qdrant_vectors=qdrant_vectors,
        queries_served=queries_served,
        avg_response_ms=round(avg_ms, 1),
        agent_invocations=agent_counts,
    )
