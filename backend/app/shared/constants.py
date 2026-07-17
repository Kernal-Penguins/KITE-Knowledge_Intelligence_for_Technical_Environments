"""
shared/constants.py
───────────────────
All numeric thresholds, model names, limits, and configuration constants.
Import from here. Never hardcode these values elsewhere.

LOCKED: Changes here affect all layers. Update tests accordingly.
"""

# ──────────────────────────────────────────────────────────────
#  Embedding & Reranking
# ──────────────────────────────────────────────────────────────
EMBEDDING_MODEL: str  = "sentence-transformers/all-MiniLM-L6-v2"
RERANKER_MODEL: str   = "cross-encoder/ms-marco-MiniLM-L-6-v2"
EMBEDDING_DIM: int    = 384          # all-MiniLM-L6-v2 output dimension

# ──────────────────────────────────────────────────────────────
#  Chunking
# ──────────────────────────────────────────────────────────────
CHUNK_SIZE_TOKENS: int    = 500
CHUNK_OVERLAP_TOKENS: int = 50

# ──────────────────────────────────────────────────────────────
#  Vector Store
# ──────────────────────────────────────────────────────────────
QDRANT_COLLECTION_NAME: str = "kite_documents"
QDRANT_TOP_K: int           = 20      # candidates fetched before reranking
QDRANT_FINAL_K: int         = 5       # top results after reranking

# ──────────────────────────────────────────────────────────────
#  Graph Retrieval
# ──────────────────────────────────────────────────────────────
MAX_GRAPH_TRAVERSAL_DEPTH: int = 3    # max hops in graph traversal

# ──────────────────────────────────────────────────────────────
#  Entity Resolution
# ──────────────────────────────────────────────────────────────
ENTITY_RESOLUTION_FUZZY_THRESHOLD: float  = 0.85   # rapidfuzz score 0–1
ENTITY_RESOLUTION_LLM_THRESHOLD: float   = 0.70   # below this → send to LLM
MAX_ALIASES_PER_NODE: int                 = 20

# ──────────────────────────────────────────────────────────────
#  Compliance Rules — Thresholds
# ──────────────────────────────────────────────────────────────
INSPECTION_MAX_AGE_DAYS: int      = 90    # CR-001: critical equipment
INCIDENT_CLOSE_DEADLINE_DAYS: int = 30   # CR-005: all incidents

# ──────────────────────────────────────────────────────────────
#  LLM Models  (Gemini)
# ──────────────────────────────────────────────────────────────
GEMINI_FLASH_MODEL: str = "gemini-2.5-flash"   # routine tasks
GEMINI_PRO_MODEL: str   = "gemini-2.5-pro"     # reasoning tasks

# ──────────────────────────────────────────────────────────────
#  Ingestion Pipeline
# ──────────────────────────────────────────────────────────────
INGESTION_MAX_RETRIES: int       = 3
INGESTION_RETRY_DELAY_SEC: float = 2.0
INGESTION_CONFIDENCE_THRESHOLD: float = 0.60   # below → flag for review

# ──────────────────────────────────────────────────────────────
#  Evaluation
# ──────────────────────────────────────────────────────────────
BENCHMARK_QUESTION_COUNT: int = 20

# ──────────────────────────────────────────────────────────────
#  Lessons-Learned Batch Scheduler
# ──────────────────────────────────────────────────────────────
LESSONS_BATCH_CRON: str            = "0 2 * * *"   # 02:00 daily
LESSONS_MIN_PATTERN_OCCURRENCES: int = 2            # min assets for a pattern
LESSONS_SIMILARITY_THRESHOLD: float  = 0.75
