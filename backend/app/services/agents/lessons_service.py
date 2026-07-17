"""
services/agents/lessons_service.py
──────────────────────────────────
Lessons Learned Agent.
Clusters historical failures and creates SIMILAR_FAILURE_MODE relationships in the graph.
"""
import asyncio

import numpy as np

from app.infrastructure.embedder import embedder
from app.infrastructure.logger import log
from app.infrastructure.neo4j_client import neo4j_client


class LessonsService:
    async def cluster_failures(self, similarity_threshold: float = 0.85) -> dict:
        log.info("lessons_service.clustering.started")
        
        failures = []
        async with neo4j_client.session() as session:
            result = await session.run("MATCH (f:Failure) RETURN f.id AS id, f.description AS desc")
            records = await result.data()
            for record in records:
                if record['desc']:
                    failures.append({"id": record['id'], "desc": record['desc']})
                    
        if len(failures) < 2:
            return {"status": "skipped", "reason": "Not enough failures to cluster"}
            
        texts = [f["desc"] for f in failures]
        vectors = await asyncio.to_thread(embedder.embed_batch, texts)
        
        edges_to_create = []
        
        def cosine_sim(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
            
        for i in range(len(failures)):
            for j in range(i + 1, len(failures)):
                sim = cosine_sim(vectors[i], vectors[j])
                if sim >= similarity_threshold:
                    edges_to_create.append({
                        "id1": failures[i]["id"],
                        "id2": failures[j]["id"],
                        "score": float(sim)
                    })
                    
        created_count = 0
        if edges_to_create:
            async with neo4j_client.session() as session:
                for edge in edges_to_create:
                    cypher = """
                    MATCH (f1:Failure {id: $id1})
                    MATCH (f2:Failure {id: $id2})
                    MERGE (f1)-[r:SIMILAR_FAILURE_MODE]->(f2)
                    ON CREATE SET r.similarity_score = $score
                    """
                    await session.run(cypher, id1=edge["id1"], id2=edge["id2"], score=edge["score"])
                    created_count += 1
                    
        log.info("lessons_service.clustering.completed", failures=len(failures), new_edges=created_count)
        
        return {
            "processed_failures": len(failures),
            "similarity_threshold": similarity_threshold,
            "new_relationships_created": created_count
        }

lessons_service = LessonsService()
