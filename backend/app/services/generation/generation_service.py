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
        
        docs_formatted = "\n".join(f"[{i}] {c}" for i, c in enumerate(chunks))
        graph_formatted = "\n".join(graph_context)
        
        prompt = f"""
        You are KITE, an industrial knowledge assistant.
        Answer the following query using ONLY the provided context.
        
        Query: {query}
        
        Text Context (Documents):
        {docs_formatted}
        
        Graph Context (Relationships):
        {graph_formatted}
        
        Provide your answer. You must include inline citations using [Doc X] or [Graph] when referencing facts.
        If the answer is not in the context, say so.
        """
        
        def _call_api():
            return self.provider.client.models.generate_content(
                model=self.provider.FLASH,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0.2,
                )
            )

        response = await asyncio.to_thread(_call_api)
        answer = response.text.strip()
        
        confidence = 0.9 if "[Doc" in answer or "[Graph]" in answer else 0.5
        
        log.info("generation_service.completed", confidence=confidence)
        
        return {
            "answer": answer,
            "confidence": confidence,
            "citations": {
                "docs": chunks,
                "graph_paths": graph_context
            }
        }

generation_service = GenerationService()
