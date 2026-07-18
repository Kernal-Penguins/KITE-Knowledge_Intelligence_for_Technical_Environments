"""
services/retrieval/hybrid_service.py
────────────────────────────────────
Combines Qdrant vector search with Neo4j graph traversal.
"""
import asyncio

from app.infrastructure.embedder import embedder
from app.infrastructure.logger import log
from app.infrastructure.neo4j_client import neo4j_client
from app.repositories.qdrant_repo import qdrant_repo


class HybridService:
    def __init__(self) -> None:
        from app.providers.gemini_provider import GeminiProvider
        self._provider = GeminiProvider()

    async def retrieve_context(self, query: str, top_k: int = 5) -> dict:
        log.info("hybrid_service.retrieving", query=query)

        query_vector = await asyncio.to_thread(embedder.embed_text, query)

        scored_points = await qdrant_repo.search(query_vector=query_vector, limit=top_k)

        chunks: list[str] = []
        node_ids: set[str] = set()

        for point in scored_points:
            payload = point.payload or {}
            text = payload.get("text", "")
            if text:
                chunks.append(text)
            for nid in payload.get("graph_node_ids", []):
                node_ids.add(nid)

        graph_context: list[str] = []
        if node_ids:
            try:
                async with neo4j_client.session() as session:
                    cypher = """
                    MATCH (n)-[r]-(m)
                    WHERE n.id IN $node_ids
                    RETURN labels(n)[0] AS n_label, n.id AS n_id,
                           type(r) AS r_type,
                           labels(m)[0] AS m_label, m.id AS m_id
                    LIMIT 50
                    """
                    result = await session.run(cypher, node_ids=list(node_ids))
                    records = await result.data()

                    for record in records:
                        relation = (
                            f"{record['n_label']}('{record['n_id']}')"
                            f" -[{record['r_type']}]->"
                            f" {record['m_label']}('{record['m_id']}')"
                        )
                        graph_context.append(relation)
            except Exception as exc:
                log.warning("hybrid_service.graph_traversal_failed", error=str(exc))

        # Filter and rerank via LLM (best-effort — fall back to raw lists on error)
        try:
            filtered_chunks = await self._provider.rerank_context(query, chunks)
            filtered_graph = await self._provider.rerank_context(query, graph_context)
        except Exception as exc:
            log.warning("hybrid_service.rerank_failed", error=str(exc))
            filtered_chunks = chunks
            filtered_graph = graph_context

        log.info(
            "hybrid_service.completed",
            chunks=len(filtered_chunks),
            graph_edges=len(filtered_graph),
        )

        return {"chunks": filtered_chunks, "graph_context": filtered_graph}


hybrid_service = HybridService()

