"""
infrastructure/embedder.py
──────────────────────────
Singleton wrapper for sentence-transformers embedding model with fallback.
"""
import hashlib
from app.infrastructure.logger import log
from app.shared.constants import EMBEDDING_MODEL


class Embedder:
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
                log.info("embedder.loading", model=EMBEDDING_MODEL)
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(EMBEDDING_MODEL)
                log.info("embedder.loaded", model=EMBEDDING_MODEL)
            except Exception as e:
                log.warning("embedder.sentence_transformers_unavailable", error=str(e))
                self._fallback = True

    def embed_text(self, text: str) -> list[float]:
        self._load_model()
        if self.model is not None:
            return self.model.encode(text).tolist()
        
        # Deterministic 384-dim fallback vector embedding
        raw_hash = hashlib.sha256(text.encode("utf-8")).digest()
        # Expand 32 byte hash to 384 floats normalized between -1.0 and 1.0
        vec = []
        for i in range(384):
            val = (raw_hash[i % 32] + (i * 17) % 256) % 256
            vec.append((val / 127.5) - 1.0)
        return vec

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        self._load_model()
        if self.model is not None:
            return self.model.encode(texts).tolist()
        return [self.embed_text(t) for t in texts]


embedder = Embedder()
