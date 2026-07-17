"""
pipeline/query_pipeline.py
──────────────────────────
Pipeline for processing a user query via GraphRAG.
"""
from app.infrastructure.logger import log
from app.services.generation.generation_service import generation_service
from app.services.retrieval.hybrid_service import hybrid_service
from app.services.retrieval.reranker_service import reranker_service


async def run_query(query: str) -> dict:
    log.info("query_pipeline.started", query=query)
    
    # 1. Retrieve Hybrid Context
    retrieval_result = await hybrid_service.retrieve_context(query, top_k=10)
    chunks = retrieval_result["chunks"]
    graph_context = retrieval_result["graph_context"]
    
    # 2. Rerank Chunks (if we have chunks and a query)
    if chunks:
        reranked = reranker_service.rerank(query, chunks, top_k=3)
        # Extract just the texts from the top 3
        top_chunks = [r["text"] for r in reranked]
    else:
        top_chunks = []
        
    # 3. Generate Answer
    response = await generation_service.generate_answer(
        query=query, 
        chunks=top_chunks, 
        graph_context=graph_context
    )
    
    log.info("query_pipeline.completed", confidence=response["confidence"])
    return response
