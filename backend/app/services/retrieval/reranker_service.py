"""
services/retrieval/reranker_service.py
──────────────────────────────────────
Cross-encoder reranker for sorting hybrid search results.
"""
from sentence_transformers import CrossEncoder

from app.infrastructure.logger import log


class RerankerService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model = None
        return cls._instance

    def _load_model(self):
        if self.model is None:
            model_name = "BAAI/bge-reranker-large"
            log.info("reranker.loading", model=model_name)
            self.model = CrossEncoder(model_name, max_length=512)
            log.info("reranker.loaded", model=model_name)

    def rerank(self, query: str, documents: list[str], top_k: int = 5) -> list[dict]:
        if not documents:
            return []
            
        self._load_model()
        
        model_inputs = [[query, doc] for doc in documents]
        scores = self.model.predict(model_inputs)
        
        scored_docs = [
            {"index": i, "score": float(score), "text": doc}
            for i, (score, doc) in enumerate(zip(scores, documents))
        ]
        
        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        return scored_docs[:top_k]

reranker_service = RerankerService()
