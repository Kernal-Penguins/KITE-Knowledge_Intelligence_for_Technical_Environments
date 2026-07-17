"""
infrastructure/embedder.py
──────────────────────────
Singleton wrapper for the sentence-transformers embedding model.
"""

from sentence_transformers import SentenceTransformer

from app.infrastructure.logger import log
from app.shared.constants import EMBEDDING_MODEL


class Embedder:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model = None
        return cls._instance

    def _load_model(self):
        if self.model is None:
            log.info("embedder.loading", model=EMBEDDING_MODEL)
            self.model = SentenceTransformer(EMBEDDING_MODEL)
            log.info("embedder.loaded", model=EMBEDDING_MODEL)

    def embed_text(self, text: str) -> list[float]:
        self._load_model()
        return self.model.encode(text).tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        self._load_model()
        return self.model.encode(texts).tolist()

embedder = Embedder()
