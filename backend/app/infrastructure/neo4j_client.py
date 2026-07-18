"""
infrastructure/neo4j_client.py
──────────────────────────────
Async Neo4j driver wrapper.
Provides a singleton driver and a context-manager session factory.

Usage:
    from app.infrastructure.neo4j_client import neo4j_client
    async with neo4j_client.session() as session:
        result = await session.run("MATCH (n) RETURN count(n)")
"""
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from neo4j import AsyncDriver, AsyncGraphDatabase, AsyncSession

from app.config import settings
from app.infrastructure.logger import log


class Neo4jClient:
    """Singleton async Neo4j driver."""

    def __init__(self) -> None:
        self._driver: AsyncDriver | None = None

    async def connect(self) -> None:
        """Open the driver connection. Called on app startup."""
        self._driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )
        await self._driver.verify_connectivity()
        await self._init_constraints()
        log.info("neo4j.connected", uri=settings.NEO4J_URI)

    async def _init_constraints(self) -> None:
        """Ensure uniqueness constraints for all node types."""
        constraints = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (e:Equipment) REQUIRE e.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (f:Failure) REQUIRE f.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Procedure) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (r:Regulation) REQUIRE r.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (i:Inspection) REQUIRE i.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (w:WorkOrder) REQUIRE w.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (i:Incident) REQUIRE i.id IS UNIQUE",
        ]
        async with self.session() as session:
            for query in constraints:
                await session.run(query)
        log.info("neo4j.constraints_initialized")

    async def close(self) -> None:
        """Close the driver. Called on app shutdown."""
        if self._driver:
            await self._driver.close()
            log.info("neo4j.disconnected")

    async def ping(self) -> bool:
        """Health check. Returns True if reachable."""
        if not self._driver:
            return False
        try:
            await self._driver.verify_connectivity()
            return True
        except Exception as exc:
            log.warning("neo4j.ping_failed", error=str(exc))
            return False

    @asynccontextmanager
    async def session(self, database: str = "neo4j") -> AsyncGenerator[AsyncSession]:
        """Yield an async Neo4j session."""
        if not self._driver:
            raise RuntimeError("Neo4j driver not initialised. Call connect() first.")
        async with self._driver.session(database=database) as session:
            yield session


neo4j_client = Neo4jClient()
