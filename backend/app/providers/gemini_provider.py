"""
providers/gemini_provider.py
────────────────────────────
Gemini implementation of LLMProvider.
"""
import asyncio

from google import genai

from app.config import settings
from app.infrastructure.logger import log
from app.providers.base import LLMProvider
from app.shared.schemas import ExtractionResult


class GeminiProvider(LLMProvider):
    FLASH = "gemini-2.5-flash"
    PRO = "gemini-2.5-pro"

    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def extract_entities(self, text: str, doc_id: str) -> ExtractionResult:
        log.info("gemini.extract_entities.started", doc_id=doc_id, model=self.FLASH)
        
        prompt = f"""
        Analyze the following text and extract industrial knowledge graph entities according to the provided schema.
        Text:
        {text}
        """

        def _call_api():
            return self.client.models.generate_content(
                model=self.FLASH,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ExtractionResult,
                    temperature=0.0,
                )
            )

        response = await asyncio.to_thread(_call_api)
        log.info("gemini.extract_entities.completed", doc_id=doc_id)
        
        result = ExtractionResult.model_validate_json(response.text)
        # Ensure doc_id is set
        result.doc_id = doc_id
        return result

    async def adjudicate_entities(self, candidate_a: str, candidate_b: str, context: str) -> str:
        pass

    async def generate_answer(self, query: str, context: list[str], citations: list) -> str:
        pass

    async def generate_rca_report(self, equipment_id: str, failure_chain: list) -> str:
        pass
