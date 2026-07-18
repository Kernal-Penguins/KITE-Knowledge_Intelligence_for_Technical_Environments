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
    """
    Execute the full hybrid query pipeline:
    1. Hybrid retrieval (vector search + graph traversal)
    2. Cross-encoder reranking
    3. LLM answer generation with citations
    """
    stripped = query.strip()
    if not stripped:
        return {
            "answer": "Please provide a question.",
            "confidence": 0.0,
            "citations": {"docs": [], "graph_paths": []},
        }

    log.info("query_pipeline.started", query=stripped)

    try:
        # 1. Hybrid retrieval
        retrieval_result = await hybrid_service.retrieve_context(stripped, top_k=10)
        chunks = retrieval_result.get("chunks", [])
        graph_context = retrieval_result.get("graph_context", [])
    except Exception as exc:
        log.error("query_pipeline.retrieval_failed", error=str(exc))
        # Fall through with empty context — LLM will say it doesn't have enough info
        chunks = []
        graph_context = []

    # 2. Rerank chunks with cross-encoder (best-effort)
    try:
        if chunks:
            reranked = reranker_service.rerank(stripped, chunks, top_k=3)
            top_chunks = [r["text"] for r in reranked]
        else:
            top_chunks = []
    except Exception as exc:
        log.warning("query_pipeline.reranking_failed", error=str(exc))
        top_chunks = chunks[:3]  # Fall back to top-3 by vector score

    # 3. Generate answer
    try:
        response = await generation_service.generate_answer(
            query=stripped,
            chunks=top_chunks,
            graph_context=graph_context,
        )
    except Exception as exc:
        log.error("query_pipeline.generation_failed", error=str(exc))
        raise  # Re-raise so the caller can return a 500

    log.info("query_pipeline.completed", confidence=response.get("confidence", 0.0))
    return response
