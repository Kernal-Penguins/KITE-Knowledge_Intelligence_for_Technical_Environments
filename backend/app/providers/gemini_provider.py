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
        """Adjudicate between two similar entity strings."""
        log.info("gemini.adjudicate.started", a=candidate_a, b=candidate_b)
        prompt = f"""
        You are an industrial knowledge graph entity resolution assistant.
        We have two candidate strings that might refer to the same entity.
        Context: {context}
        Candidate A: '{candidate_a}'
        Candidate B: '{candidate_b}'
        
        If they refer to the same entity, return the best, most canonical name.
        If they refer to different entities, reply strictly with 'DIFFERENT'.
        Return ONLY the resolved string or 'DIFFERENT', with no extra text.
        """
        
        def _call_api():
            return self.client.models.generate_content(
                model=self.FLASH,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0.0,
                )
            )

        response = await asyncio.to_thread(_call_api)
        result = response.text.strip()
        log.info("gemini.adjudicate.completed", result=result)
        return result

    async def rerank_context(self, query: str, context: list[str]) -> list[str]:
        """Rerank and filter context chunks/edges based on relevance to query."""
        if not context:
            return []
            
        log.info("gemini.rerank_context.started", query=query, context_size=len(context))
        
        context_str = "\n".join([f"[{i}] {c}" for i, c in enumerate(context)])
        prompt = f"""
        You are a relevance filtering assistant.
        Query: '{query}'
        
        Context Items:
        {context_str}
        
        Identify ONLY the indices of the context items that are relevant or potentially helpful for answering the query.
        Return your answer as a JSON array of integers, e.g. [0, 2, 5]. If none are relevant, return [].
        Do not include any other text.
        """
        
        def _call_api():
            return self.client.models.generate_content(
                model=self.FLASH,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.0,
                )
            )

        try:
            response = await asyncio.to_thread(_call_api)
            import json
            indices = json.loads(response.text)
            filtered_context = [context[i] for i in indices if 0 <= i < len(context)]
            log.info("gemini.rerank_context.completed", original_size=len(context), filtered_size=len(filtered_context))
            return filtered_context
        except Exception as e:
            log.error("gemini.rerank_context.failed", error=str(e))
            # Fallback to returning original context if reranking fails
            return context

    async def generate_answer(self, query: str, context: list[str], citations: list) -> str:
        pass

    async def generate_rca_report(self, equipment_id: str, failure_chain: list) -> str:
        pass
