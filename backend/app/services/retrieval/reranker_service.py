"""
services/retrieval/reranker_service.py
──────────────────────────────────────
Cross-encoder reranker for sorting hybrid search results with fallback.
"""
from app.infrastructure.logger import log
from app.shared.constants import RERANKER_MODEL


class RerankerService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model = None
            cls._instance._fallback = False
        return cls._instance

    def _load_model(self):
        if self.model is None and not self._fallback:
            try:
                log.info("reranker.loading", model=RERANKER_MODEL)
                from sentence_transformers import CrossEncoder
                self.model = CrossEncoder(RERANKER_MODEL, max_length=512)
                log.info("reranker.loaded", model=RERANKER_MODEL)
            except Exception as e:
                log.warning("reranker.unavailable_using_fallback", error=str(e))
                self._fallback = True

    def rerank(self, query: str, documents: list[str], top_k: int = 5) -> list[dict]:
        if not documents:
            return []
            
        self._load_model()
        if self.model is not None:
            model_inputs = [[query, doc] for doc in documents]
            scores = self.model.predict(model_inputs)
            scored_docs = [
                {"index": i, "score": float(score), "text": doc}
                for i, (score, doc) in enumerate(zip(scores, documents))
            ]
            scored_docs.sort(key=lambda x: x["score"], reverse=True)
            return scored_docs[:top_k]

        # Heuristic term-overlap fallback
        query_terms = set(query.lower().split())
        scored_docs = []
        for i, doc in enumerate(documents):
            doc_terms = set(doc.lower().split())
            score = len(query_terms.intersection(doc_terms)) / (len(query_terms) + 1.0)
            scored_docs.append({"index": i, "score": float(score), "text": doc})
        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        return scored_docs[:top_k]


reranker_service = RerankerService()
