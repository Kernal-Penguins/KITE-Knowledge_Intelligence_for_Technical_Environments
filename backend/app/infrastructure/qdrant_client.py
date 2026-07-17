"""
infrastructure/qdrant_client.py
────────────────────────────────
Async Qdrant client wrapper.

Usage:
    from app.infrastructure.qdrant_client import qdrant_client
"""
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Distance, VectorParams

from app.config import settings
from app.infrastructure.logger import log
from app.shared.constants import EMBEDDING_DIM, QDRANT_COLLECTION_NAME


class QdrantClientWrapper:
    """Singleton async Qdrant client."""

    def __init__(self) -> None:
        self._client: AsyncQdrantClient | None = None

    async def connect(self) -> None:
        """Initialise client and ensure collection exists. Called on app startup."""
        kwargs = {"url": settings.QDRANT_URL}
        if settings.QDRANT_API_KEY:
            kwargs["api_key"] = settings.QDRANT_API_KEY

        self._client = AsyncQdrantClient(**kwargs)

        # Ensure collection exists
        existing = await self._client.get_collections()
        existing_names = [c.name for c in existing.collections]
        if QDRANT_COLLECTION_NAME not in existing_names:
            await self._client.create_collection(
                collection_name=QDRANT_COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=EMBEDDING_DIM,
                    distance=Distance.COSINE,
                ),
            )
            log.info("qdrant.collection_created", collection=QDRANT_COLLECTION_NAME)

        log.info("qdrant.connected", url=settings.QDRANT_URL)

    async def close(self) -> None:
        if self._client:
            await self._client.close()
            log.info("qdrant.disconnected")

    async def ping(self) -> bool:
        try:
            await self._client.get_collections()
            return True
        except Exception as exc:
            log.warning("qdrant.ping_failed", error=str(exc))
            return False

    @property
    def client(self) -> AsyncQdrantClient:
        if not self._client:
            raise RuntimeError("Qdrant client not initialised. Call connect() first.")
        return self._client


qdrant_client = QdrantClientWrapper()
