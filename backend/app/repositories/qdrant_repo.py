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
        try:
            from qdrant_client.http.models import SearchRequest
            res = await client.http.search_api.search_points(
                collection_name=QDRANT_COLLECTION_NAME,
                search_request=SearchRequest(vector=query_vector, limit=limit, with_payload=True),
            )
            return res.result
        except Exception as e:
            from app.infrastructure.logger import log
            log.warning("qdrant_repo.search_failed", error=str(e))
            return []

qdrant_repo = QdrantRepo()
