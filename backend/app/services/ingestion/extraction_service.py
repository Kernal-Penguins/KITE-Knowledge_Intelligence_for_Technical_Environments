"""
services/ingestion/extraction_service.py
────────────────────────────────────────
Service to extract structured entities from raw document text.
"""
from app.infrastructure.logger import log
from app.providers.gemini_provider import GeminiProvider
from app.shared.schemas import ExtractionResult


class ExtractionService:
    def __init__(self):
        self.provider = GeminiProvider()

    async def run_extraction(self, text: str, doc_id: str) -> ExtractionResult:
        """Pass markdown text to the LLM to extract Knowledge Graph entities."""
        log.info("extraction_service.started", doc_id=doc_id)
        
        result = await self.provider.extract_entities(text=text, doc_id=doc_id)
        
        log.info(
            "extraction_service.completed",
            doc_id=doc_id,
            equipment=len(result.equipment),
            failures=len(result.failures),
            procedures=len(result.procedures),
            personnel=len(result.personnel),
        )
        return result

extraction_service = ExtractionService()
