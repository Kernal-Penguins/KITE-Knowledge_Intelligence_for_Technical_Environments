"""
repositories/qdrant_repo.py
───────────────────────────
Vector repository for document chunks.
"""

from qdrant_client.http.models import PointStruct, ScoredPoint

from app.infrastructure.qdrant_client import qdrant_client
from app.shared.constants import QDRANT_COLLECTION_NAME


class QdrantRepo:
    """Repository for vector operations in Qdrant."""

    @staticmethod
    async def upsert_chunks(points: list[PointStruct]):
        """Upsert a batch of vectors with payload to Qdrant."""
        client = qdrant_client.client
        return await client.upsert(
            collection_name=QDRANT_COLLECTION_NAME,
            points=points
        )

    @staticmethod
    async def search(query_vector: list[float], limit: int = 5) -> list[ScoredPoint]:
        """Search for the most similar chunks."""
        client = qdrant_client.client
        return await client.search(
            collection_name=QDRANT_COLLECTION_NAME,
            query_vector=query_vector,
            limit=limit,
        )

qdrant_repo = QdrantRepo()
