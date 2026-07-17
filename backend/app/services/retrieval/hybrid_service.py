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
    async def retrieve_context(self, query: str, top_k: int = 5) -> dict:
        log.info("hybrid_service.retrieving", query=query)
        
        query_vector = await asyncio.to_thread(embedder.embed_text, query)
        
        scored_points = await qdrant_repo.search(query_vector=query_vector, limit=top_k)
        
        chunks = []
        node_ids = set()
        
        for point in scored_points:
            payload = point.payload or {}
            text = payload.get("text", "")
            chunks.append(text)
            
            for nid in payload.get("graph_node_ids", []):
                node_ids.add(nid)
                
        graph_context = []
        if node_ids:
            async with neo4j_client.session() as session:
                cypher = """
                MATCH (n)-[r]-(m)
                WHERE n.id IN $node_ids
                RETURN labels(n)[0] AS n_label, n.id AS n_id, type(r) AS r_type, labels(m)[0] AS m_label, m.id AS m_id
                LIMIT 50
                """
                result = await session.run(cypher, node_ids=list(node_ids))
                records = await result.data()
                
                for record in records:
                    relation = f"{record['n_label']}('{record['n_id']}') -[{record['r_type']}]-> {record['m_label']}('{record['m_id']}')"
                    graph_context.append(relation)
                    
        log.info("hybrid_service.completed", chunks=len(chunks), graph_edges=len(graph_context))
        
        return {
            "chunks": chunks,
            "graph_context": graph_context
        }

hybrid_service = HybridService()
