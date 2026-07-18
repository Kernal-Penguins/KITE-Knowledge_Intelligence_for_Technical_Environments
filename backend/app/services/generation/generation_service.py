"""
services/generation/generation_service.py
─────────────────────────────────────────
Uses the Gemini Provider to generate an answer with citations.
"""
import asyncio

from google import genai

from app.infrastructure.logger import log
from app.providers.gemini_provider import GeminiProvider


class GenerationService:
    def __init__(self):
        self.provider = GeminiProvider()

    async def generate_answer(self, query: str, chunks: list[str], graph_context: list[str]) -> dict:
        log.info("generation_service.started", query=query)
        return await self.provider.generate_answer(query, chunks, graph_context)

generation_service = GenerationService()
