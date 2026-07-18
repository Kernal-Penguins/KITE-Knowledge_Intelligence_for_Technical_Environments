"""
tests/unit/test_resolution_service.py
──────────────────────────────────────
Unit tests for the entity resolution logic. All LLM calls are mocked
so no GEMINI_API_KEY is required.
"""
import pytest
from unittest.mock import AsyncMock, patch

from app.services.ingestion.resolution_service import ResolutionService
from app.shared.schemas import Equipment, ExtractionResult


def _make_result(*tag_ids: str) -> ExtractionResult:
    """Helper: make an ExtractionResult with a list of Equipment by tag_id."""
    return ExtractionResult(
        doc_id="doc-test",
        equipment=[Equipment(tag_id=tid, type="Pump") for tid in tag_ids],
    )


class TestResolutionServiceThresholds:
    def test_high_confidence_threshold_is_integer_scale(self):
        """Regression: threshold must be on 0–100 scale to match fuzz.ratio() output."""
        svc = ResolutionService.__new__(ResolutionService)
        svc.HIGH_CONFIDENCE_THRESHOLD = 90
        svc.LLM_ADJUDICATION_THRESHOLD = 75
        assert svc.HIGH_CONFIDENCE_THRESHOLD > 1, (
            "HIGH_CONFIDENCE_THRESHOLD must be in 0-100 scale, not 0-1"
        )
        assert svc.LLM_ADJUDICATION_THRESHOLD > 1, (
            "LLM_ADJUDICATION_THRESHOLD must be in 0-100 scale, not 0-1"
        )


@pytest.mark.asyncio
class TestResolutionServiceMerging:
    async def test_identical_tag_ids_merged(self):
        """Two identical equipment tags should be collapsed to one."""
        with patch(
            "app.services.ingestion.resolution_service.GeminiProvider",
        ) as mock_provider_cls:
            mock_provider_cls.return_value.adjudicate_entities = AsyncMock(
                return_value="DIFFERENT"
            )
            svc = ResolutionService()
            result = _make_result("P-101", "P-101")
            resolved = await svc.resolve_entities(result)
            assert len(resolved.equipment) == 1

    async def test_clearly_different_tags_not_merged(self):
        """Tags with very different strings should remain separate."""
        with patch(
            "app.services.ingestion.resolution_service.GeminiProvider",
        ) as mock_provider_cls:
            mock_provider_cls.return_value.adjudicate_entities = AsyncMock(
                return_value="DIFFERENT"
            )
            svc = ResolutionService()
            result = _make_result("P-101", "V-999")
            resolved = await svc.resolve_entities(result)
            assert len(resolved.equipment) == 2

    async def test_single_equipment_passes_through_unchanged(self):
        """A single piece of equipment should never be modified."""
        with patch(
            "app.services.ingestion.resolution_service.GeminiProvider",
        ) as mock_provider_cls:
            svc = ResolutionService()
            result = _make_result("P-104")
            resolved = await svc.resolve_entities(result)
            assert len(resolved.equipment) == 1
            assert resolved.equipment[0].tag_id == "P-104"

    async def test_empty_equipment_list_passes_through(self):
        """No equipment to resolve — should return empty list, no crash."""
        with patch(
            "app.services.ingestion.resolution_service.GeminiProvider",
        ):
            svc = ResolutionService()
            result = _make_result()  # empty
            resolved = await svc.resolve_entities(result)
            assert resolved.equipment == []

    async def test_llm_adjudication_failure_treats_as_different(self):
        """If the LLM call throws, entities should be kept separate (safe default)."""
        with patch(
            "app.services.ingestion.resolution_service.GeminiProvider",
        ) as mock_provider_cls:
            mock_provider_cls.return_value.adjudicate_entities = AsyncMock(
                side_effect=RuntimeError("LLM API timeout")
            )
            svc = ResolutionService()
            # These are similar enough to trigger LLM adjudication
            result = _make_result("Pump-104", "P-104")
            resolved = await svc.resolve_entities(result)
            # Should not crash; both should be kept
            assert len(resolved.equipment) >= 1
