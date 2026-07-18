"""
tests/unit/test_constants.py
─────────────────────────────
Validate that shared/constants.py values are sensible.
These act as a regression guard against accidental mis-edits.
"""
import pytest

from app.shared.constants import (
    BENCHMARK_QUESTION_COUNT,
    CHUNK_OVERLAP_TOKENS,
    CHUNK_SIZE_TOKENS,
    EMBEDDING_DIM,
    EMBEDDING_MODEL,
    ENTITY_RESOLUTION_FUZZY_THRESHOLD,
    ENTITY_RESOLUTION_LLM_THRESHOLD,
    INCIDENT_CLOSE_DEADLINE_DAYS,
    INGESTION_CONFIDENCE_THRESHOLD,
    INGESTION_MAX_RETRIES,
    INSPECTION_MAX_AGE_DAYS,
    LESSONS_SIMILARITY_THRESHOLD,
    MAX_ALIASES_PER_NODE,
    MAX_GRAPH_TRAVERSAL_DEPTH,
    QDRANT_COLLECTION_NAME,
    QDRANT_FINAL_K,
    QDRANT_TOP_K,
    RERANKER_MODEL,
)


class TestChunkingConstants:
    def test_chunk_overlap_smaller_than_chunk_size(self):
        assert CHUNK_OVERLAP_TOKENS < CHUNK_SIZE_TOKENS, (
            "Overlap must be less than chunk size to avoid infinite loops"
        )

    def test_chunk_size_positive(self):
        assert CHUNK_SIZE_TOKENS > 0

    def test_overlap_positive(self):
        assert CHUNK_OVERLAP_TOKENS > 0


class TestRetrievalConstants:
    def test_final_k_lte_top_k(self):
        assert QDRANT_FINAL_K <= QDRANT_TOP_K, (
            "QDRANT_FINAL_K (post-rerank) must not exceed QDRANT_TOP_K (pre-rerank candidates)"
        )

    def test_collection_name_non_empty(self):
        assert QDRANT_COLLECTION_NAME.strip() != ""

    def test_embedding_dim_positive(self):
        assert EMBEDDING_DIM > 0

    def test_graph_traversal_depth_sensible(self):
        assert 1 <= MAX_GRAPH_TRAVERSAL_DEPTH <= 10


class TestEntityResolutionConstants:
    def test_thresholds_in_zero_to_one_range(self):
        """These are used as 0-1 fractions in constants.py (not as fuzz.ratio scores)."""
        assert 0.0 < ENTITY_RESOLUTION_FUZZY_THRESHOLD <= 1.0
        assert 0.0 < ENTITY_RESOLUTION_LLM_THRESHOLD <= 1.0

    def test_llm_threshold_lower_than_fuzzy(self):
        """LLM kicks in for ambiguous cases — should be the lower threshold."""
        assert ENTITY_RESOLUTION_LLM_THRESHOLD < ENTITY_RESOLUTION_FUZZY_THRESHOLD

    def test_max_aliases_sensible(self):
        assert MAX_ALIASES_PER_NODE >= 5


class TestComplianceConstants:
    def test_inspection_max_age_positive(self):
        assert INSPECTION_MAX_AGE_DAYS > 0

    def test_incident_close_deadline_positive(self):
        assert INCIDENT_CLOSE_DEADLINE_DAYS > 0


class TestIngestionConstants:
    def test_max_retries_sensible(self):
        assert 0 < INGESTION_MAX_RETRIES <= 10

    def test_confidence_threshold_in_range(self):
        assert 0.0 <= INGESTION_CONFIDENCE_THRESHOLD <= 1.0


class TestModelNames:
    def test_embedding_model_non_empty(self):
        assert EMBEDDING_MODEL.strip() != ""

    def test_reranker_model_non_empty(self):
        assert RERANKER_MODEL.strip() != ""
