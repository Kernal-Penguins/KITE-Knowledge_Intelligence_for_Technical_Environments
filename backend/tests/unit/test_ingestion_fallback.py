"""Ingest must finish for a plain-text maintenance log when the LLM is down."""
import asyncio
from pathlib import Path

from app.providers.gemini_provider import (
    GeminiProvider,
    _fallback_entity_extraction,
    _parse_extraction_response,
)
from app.services.ingestion.parser_service import ParserService

SAMPLE = """
MAINTENANCE LOG ENTRY
Equipment: P-104 (Centrifugal Pump, Unit 3 - Process Water Transfer)
Date: 2025-04-12
Description:
Operator reported visible leakage from mechanical seal area on P-104.
Work order WO-10201 opened for tracking.
"""


def test_plain_text_parser_does_not_call_docling(tmp_path: Path):
    path = tmp_path / "ML-P104.txt"
    path.write_text(SAMPLE, encoding="utf-8")
    parser = ParserService()
    parser._docling_available = False
    text = parser.parse_document(path)
    assert "P-104" in text
    assert "WO-10201" in text


def test_fallback_extracts_equipment_failure_and_work_order():
    result = _fallback_entity_extraction(SAMPLE, "doc-abc123")
    assert [item.tag_id for item in result.equipment] == ["P-104"]
    assert result.equipment[0].type == "Centrifugal Pump"
    assert result.failures[0].equipment_tag == "P-104"
    assert result.failures[0].date is not None
    assert result.failures[0].date.isoformat() == "2025-04-12"
    assert result.work_orders[0].wo_id == "WO-10201"
    assert result.relationships


def test_partial_model_json_keeps_valid_equipment():
    raw = """
    {
      "doc_id": "ignored",
      "equipment": [
        {"tag_id": "CV-220", "type": "Control Valve", "aliases": null, "criticality": "HIGH"}
      ],
      "failures": [
        {"failure_id": null, "description": "leak", "equipment_tag": "CV-220", "date": "not-a-date"}
      ]
    }
    """
    result = _parse_extraction_response(raw, "doc-xyz987")
    assert result is not None
    assert result.doc_id == "doc-xyz987"
    assert result.equipment[0].tag_id == "CV-220"
    assert result.equipment[0].criticality.value == "High"
    assert result.failures == []


def test_extract_entities_falls_back_when_gemini_errors():
    provider = GeminiProvider()

    class _BrokenModels:
        def generate_content(self, **kwargs):
            raise RuntimeError("API key not valid")

    class _BrokenClient:
        models = _BrokenModels()

    provider.client = _BrokenClient()
    result = asyncio.run(provider.extract_entities(SAMPLE, "doc-abc123"))
    assert result.equipment[0].tag_id == "P-104"
    assert result.work_orders[0].wo_id == "WO-10201"


def test_gemini_client_uses_json_mode_api_version(monkeypatch):
    from app.config import settings
    from app.providers import gemini_provider as gp

    captured: dict = {}

    class FakeClient:
        def __init__(self, *, api_key, http_options):
            captured["api_key"] = api_key
            captured["http_options"] = http_options

    monkeypatch.setattr(gp.genai, "Client", FakeClient)
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "test-key")
    provider = gp.GeminiProvider()
    assert provider.client is not None
    assert captured["api_key"] == "test-key"
    # conftest stubs google.genai, so assert the kwargs passed to HttpOptions.
    assert gp.genai.types.HttpOptions.call_args.kwargs["api_version"] == "v1beta"


def test_api_key_strips_quotes():
    from app.config import Settings

    settings = Settings(GEMINI_API_KEY='  "your_key_here"  ')
    assert settings.GEMINI_API_KEY == ""
    settings = Settings(GEMINI_API_KEY="'abc-real-key'")
    assert settings.GEMINI_API_KEY == "abc-real-key"
