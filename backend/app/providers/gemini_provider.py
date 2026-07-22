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
import re
from app.shared.schemas import Equipment, Failure, ExtractionResult


def _fallback_entity_extraction(text: str, doc_id: str) -> ExtractionResult:
    """Regex fallback to extract key equipment & failure entities when LLM API rate limits occur."""
    tags = set(re.findall(r'\b(?:P-\d+|CV-\d+|CB-\d+|TK-\d+|GEN-\d+|AC-\d+|FN-\d+|MTR-\d+|Pump \d+|Control Valve \d+|Conveyor \d+)\b', text, re.IGNORECASE))
    equipment_list = [Equipment(tag_id=t, type="Industrial Equipment", source_doc_ids=[doc_id]) for t in tags]
    
    failures = []
    if any(k in text.lower() for k in ["fail", "leak", "overheat", "seizure", "damage", "vibration"]):
        for t in tags:
            failures.append(Failure(failure_id=f"F-{doc_id[-6:]}", description=text[:200], equipment_tag=t, source_doc_ids=[doc_id]))
            
    return ExtractionResult(
        doc_id=doc_id,
        equipment=equipment_list,
        failures=failures,
        extraction_confidence=0.7,
        extraction_errors=["Rate-limited by LLM API; used heuristic fallback"]
    )


def _get_cleaned_extraction_schema():
    schema = ExtractionResult.model_json_schema()
    def _strip_additional_properties(d):
        if isinstance(d, dict):
            d.pop("additionalProperties", None)
            for v in d.values():
                _strip_additional_properties(v)
        elif isinstance(d, list):
            for item in d:
                _strip_additional_properties(item)
        return d
    return _strip_additional_properties(schema)


class GeminiProvider(LLMProvider):
    FLASH = "gemini-2.0-flash"
    PRO = "gemini-1.5-pro"
    FLASH_MODELS = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]

    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self._cleaned_schema = _get_cleaned_extraction_schema()

    async def extract_entities(self, text: str, doc_id: str) -> ExtractionResult:
        log.info("gemini.extract_entities.started", doc_id=doc_id)
        
        prompt = f"""
        Analyze the following text and extract industrial knowledge graph entities according to the provided schema.
        Text:
        {text}
        """

        async def _call_api_with_retry():
            for outer_attempt in range(2):
                for model_name in self.FLASH_MODELS:
                    for attempt in range(2):
                        try:
                            log.info("gemini.extract_entities.trying", doc_id=doc_id, model=model_name, attempt=attempt+1)
                            return await asyncio.to_thread(
                                self.client.models.generate_content,
                                model=model_name,
                                contents=prompt,
                                config=genai.types.GenerateContentConfig(
                                    response_mime_type="application/json",
                                    response_schema=self._cleaned_schema,
                                    temperature=0.0,
                                )
                            )
                        except Exception as e:
                            err_msg = str(e)
                            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                                log.warning("gemini.extract_entities.rate_limited", model=model_name, attempt=attempt+1)
                                if attempt == 0:
                                    await asyncio.sleep(1.0)
                                else:
                                    break
                            else:
                                raise e
                log.warning("gemini.extract_entities.all_models_rate_limited", outer_attempt=outer_attempt+1, wait_sec=2.0)
                await asyncio.sleep(2.0)
            return None

        response = await _call_api_with_retry()
        if response is None:
            log.warning("gemini.extract_entities.fallback_to_heuristics", doc_id=doc_id)
            return _fallback_entity_extraction(text, doc_id)

        log.info("gemini.extract_entities.completed", doc_id=doc_id)
        result = ExtractionResult.model_validate_json(response.text)
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

    async def generate_answer(self, query: str, chunks: list[str], graph_context: list[str]) -> dict:
        log.info("gemini.generate_answer.started", query=query)
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

        async def _call_api_with_retry():
            for outer in range(2):
                for model_name in self.FLASH_MODELS:
                    for attempt in range(2):
                        try:
                            return await asyncio.to_thread(
                                self.client.models.generate_content,
                                model=model_name,
                                contents=prompt,
                                config=genai.types.GenerateContentConfig(temperature=0.2)
                            )
                        except Exception as e:
                            err_msg = str(e)
                            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                                await asyncio.sleep(2.0)
                            else:
                                raise e
                await asyncio.sleep(5.0)
            return None

        try:
            response = await _call_api_with_retry()
            if response and response.text:
                answer = response.text.strip()
            else:
                answer = f"Based on knowledge graph & context: {docs_formatted[:250]} {graph_formatted[:250]}"
        except Exception as exc:
            log.warning("gemini.generate_answer.fallback", error=str(exc))
            answer = f"Retrieved Knowledge Graph Context for '{query}': {docs_formatted[:250]} {graph_formatted[:250]}"

        confidence = 0.9 if ("[Doc" in answer or "[Graph]" in answer) else 0.6
        return {
            "answer": answer,
            "confidence": confidence,
            "citations": {
                "docs": chunks,
                "graph_paths": graph_context
            }
        }

    async def generate_rca_report(self, equipment_id: str, failure_chain: list) -> str:
        return f"RCA Report for {equipment_id}: Failure events identified: {failure_chain}"
