"""
providers/groq_provider.py
──────────────────────────
Groq implementation of LLMProvider (Stub).
"""
from app.providers.base import LLMProvider
from app.shared.schemas import ExtractionResult


class GroqProvider(LLMProvider):
    async def extract_entities(self, text: str, doc_id: str) -> ExtractionResult:
        raise NotImplementedError("Groq provider not yet implemented.")

    async def adjudicate_entities(self, candidate_a: str, candidate_b: str, context: str) -> str:
        raise NotImplementedError()

    async def generate_answer(self, query: str, context: list[str], citations: list) -> str:
        raise NotImplementedError()

    async def generate_rca_report(self, equipment_id: str, failure_chain: list) -> str:
        raise NotImplementedError()
