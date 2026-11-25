"""
providers/gemini_provider.py
────────────────────────────
Gemini implementation of LLMProvider.
"""
import asyncio
import json
import re

from google import genai

from app.config import settings
from app.infrastructure.logger import log
from app.providers.base import LLMProvider
from app.shared.ontology import NodeLabel, RelType
from app.shared.schemas import Equipment, ExtractionResult, Failure, Relationship, WorkOrder

_TAG_RE = re.compile(r"\b(?:P|CV|CB|TK|GEN|AC|FN|MTR|HX)-\d+\b", re.IGNORECASE)
_WO_RE = re.compile(r"\bWO-\d+\b", re.IGNORECASE)
_DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
_LEVELS = {"low": "Low", "medium": "Medium", "high": "High", "critical": "Critical"}
_FAILURE_WORDS = ("fail", "leak", "overheat", "seizure", "damage", "vibration", "scoring")


def _opt_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _opt_level(value: object) -> str | None:
    text = _opt_str(value)
    if text is None:
        return None
    return _LEVELS.get(text.lower())


def _opt_date(value: object) -> str | None:
    text = _opt_str(value)
    if text is None:
        return None
    match = _DATE_RE.search(text)
    return match.group(1) if match else None


def _fallback_entity_extraction(text: str, doc_id: str) -> ExtractionResult:
    """Pull equipment tags and work orders from the document when the LLM is unavailable."""
    tags: list[str] = []
    seen: set[str] = set()
    for match in _TAG_RE.findall(text):
        tag = match.upper()
        if tag not in seen:
            seen.add(tag)
            tags.append(tag)

    equipment: list[Equipment] = []
    for tag in tags:
        detail = re.search(rf"{re.escape(tag)}\s*\(([^)]+)\)", text, re.IGNORECASE)
        eq_type = "Industrial Equipment"
        if detail:
            eq_type = detail.group(1).split(",")[0].strip() or eq_type
        equipment.append(Equipment(tag_id=tag, type=eq_type, source_doc_ids=[doc_id]))

    date = _DATE_RE.search(text)
    iso_date = date.group(1) if date else None
    summary = next((line.strip() for line in text.splitlines() if line.strip()), "Failure noted")[:200]

    failures: list[Failure] = []
    if any(word in text.lower() for word in _FAILURE_WORDS):
        for tag in tags:
            failures.append(
                Failure(
                    failure_id=f"F-{tag}-{doc_id[-6:]}",
                    description=summary,
                    equipment_tag=tag,
                    date=iso_date,
                    source_doc_ids=[doc_id],
                )
            )

    work_orders: list[WorkOrder] = []
    for wo_id in dict.fromkeys(match.upper() for match in _WO_RE.findall(text)):
        work_orders.append(
            WorkOrder(
                wo_id=wo_id,
                date=iso_date,
                description="Work order referenced in the document",
                source_doc_ids=[doc_id],
            )
        )

    relationships: list[Relationship] = []
    for failure in failures:
        relationships.append(
            Relationship(
                from_id=failure.equipment_tag,
                from_label=NodeLabel.EQUIPMENT,
                to_id=failure.failure_id,
                to_label=NodeLabel.FAILURE,
                rel_type=RelType.HAS_FAILURE,
                source_doc_ids=[doc_id],
            )
        )
        if work_orders:
            relationships.append(
                Relationship(
                    from_id=failure.failure_id,
                    from_label=NodeLabel.FAILURE,
                    to_id=work_orders[0].wo_id,
                    to_label=NodeLabel.WORK_ORDER,
                    rel_type=RelType.RESOLVED_BY,
                    source_doc_ids=[doc_id],
                )
            )

    return ExtractionResult(
        doc_id=doc_id,
        equipment=equipment,
        failures=failures,
        work_orders=work_orders,
        relationships=relationships,
        extraction_confidence=0.7,
        extraction_errors=["LLM extraction unavailable; used document text fallback"],
    )


def _salvage_extraction(payload: object, doc_id: str) -> ExtractionResult | None:
    """Keep valid entities when the model JSON does not match the full schema."""
    if not isinstance(payload, dict):
        return None

    equipment: list[Equipment] = []
    for item in payload.get("equipment") or []:
        if not isinstance(item, dict):
            continue
        tag = _opt_str(item.get("tag_id"))
        if not tag:
            continue
        try:
            equipment.append(
                Equipment(
                    tag_id=tag,
                    type=_opt_str(item.get("type")) or "Equipment",
                    location=_opt_str(item.get("location")),
                    criticality=_opt_level(item.get("criticality")),
                    aliases=[str(alias) for alias in (item.get("aliases") or []) if alias],
                    source_doc_ids=[doc_id],
                )
            )
        except Exception:
            continue

    failures: list[Failure] = []
    for item in payload.get("failures") or []:
        if not isinstance(item, dict):
            continue
        failure_id = _opt_str(item.get("failure_id"))
        equipment_tag = _opt_str(item.get("equipment_tag"))
        description = _opt_str(item.get("description"))
        if not failure_id or not equipment_tag or not description:
            continue
        try:
            failures.append(
                Failure(
                    failure_id=failure_id,
                    description=description,
                    equipment_tag=equipment_tag,
                    date=_opt_date(item.get("date")),
                    severity=_opt_level(item.get("severity")),
                    source_doc_ids=[doc_id],
                )
            )
        except Exception:
            continue

    if not equipment and not failures:
        return None

    return ExtractionResult(
        doc_id=doc_id,
        equipment=equipment,
        failures=failures,
        extraction_confidence=0.8,
        extraction_errors=["Model JSON was partial; kept the entities that validated"],
    )


def _parse_extraction_response(raw: str, doc_id: str) -> ExtractionResult | None:
    try:
        result = ExtractionResult.model_validate_json(raw)
        result.doc_id = doc_id
        return result
    except Exception:
        pass
    try:
        return _salvage_extraction(json.loads(raw), doc_id)
    except Exception:
        return None


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
    FLASH = "gemini-2.5-flash"
    PRO = "gemini-2.5-pro"
    FLASH_MODELS = [
        "gemini-2.5-flash",
        "gemini-2.5-pro",
    ]

    def __init__(self):
        self.client = None
        self._cleaned_schema = _get_cleaned_extraction_schema()
        key = settings.GEMINI_API_KEY.strip()
        if not key:
            log.warning("gemini.api_key_missing")
            return
        try:
            self.client = genai.Client(
                api_key=key,
                http_options=genai.types.HttpOptions(timeout=30_000),
            )
        except Exception as exc:
            log.warning("gemini.client_init_failed", error=str(exc))
            self.client = None

    async def extract_entities(self, text: str, doc_id: str) -> ExtractionResult:
        log.info("gemini.extract_entities.started", doc_id=doc_id)
        
        prompt = f"""
                    You are KITE (Knowledge Integration & Tracing Engine), an Industrial Knowledge Graph Extraction Engine.

Your task is to extract structured industrial maintenance knowledge from the document.

Return ONLY valid JSON matching the provided response schema.

=========================
NODE TYPES
=========================

Extract every entity belonging to these categories:

• Equipment
Examples:
Pump, Motor, Compressor, Valve, Control Valve, Conveyor, Gearbox,
Tank, Generator, Turbine, Fan, Boiler, Heat Exchanger, Pipeline,
Electrical Panel, Sensor.

Use the equipment tag exactly as written (e.g. P-101, CV-220, GEN-04).
Never invent equipment IDs.

• Failure
Examples:
Leak, Oil Leak, Seal Failure, Bearing Failure, Corrosion,
Overheating, High Temperature, Cavitation, Vibration,
Blockage, Mechanical Failure, Electrical Failure,
Motor Trip, Seizure, Wear.

Include:
- description
- equipment_tag
- severity (if mentioned)
- date (if available)

• WorkOrder
Extract:
- work order ID
- status
- date
- description

• Inspection
Extract:
- inspection ID
- equipment
- inspector
- date
- result

• Procedure
Extract:
- procedure ID
- title
- version
- governing regulation

• Regulation
Examples:
API, ISO, IEC, OSHA, OISD, ASME.

Extract:
- regulation ID
- source
- clause

• Person
Extract:
- person ID
- name
- role
- certification

• Incident
Extract:
- incident ID
- description
- severity
- date

=========================
RELATIONSHIPS
=========================

Create ONLY these relationships when explicitly supported by the document.

Equipment HAS_FAILURE Failure

Failure RESOLVED_BY WorkOrder

Inspection INSPECTED_ON Equipment

Person PERFORMED_BY Inspection

Procedure GOVERNED_BY Regulation

Incident REFERENCES Failure

Failure SIMILAR_FAILURE_MODE Failure

Do NOT invent relationships.

If a relationship is uncertain, omit it.

=========================
NORMALIZATION
=========================

Normalize equivalent equipment references.

Examples:

Pump-101 -> P-101

CV220 -> CV-220

Generator-04 -> GEN-04

Use the canonical equipment tag whenever possible.

=========================
DATES
=========================

Convert dates to ISO format:

YYYY-MM-DD

If unavailable:

null

=========================
SEVERITY
=========================

Map severity to one of:

LOW

MEDIUM

HIGH

CRITICAL

Otherwise use null.

=========================
CONFIDENCE
=========================

Estimate extraction_confidence between 0.0 and 1.0.

=========================
IMPORTANT RULES
=========================

Extract every supported entity.

Never hallucinate.

Never invent IDs.

Never invent relationships.

Never guess missing information.

If information is missing, use null or leave the field empty.

Before generating the JSON, internally verify that every relationship references entities that actually exist in the extracted output.

Return ONLY JSON.

DOCUMENT

{text}
"""

        async def _call_api_with_retry():
            if self.client is None:
                return None
            last_error = "no attempt"
            for model_name in self.FLASH_MODELS:
                try:
                    log.info("gemini.extract_entities.trying", doc_id=doc_id, model=model_name)
                    return await asyncio.wait_for(
                        asyncio.to_thread(
                            self.client.models.generate_content,
                            model=model_name,
                            contents=prompt,
                            config=genai.types.GenerateContentConfig(
                                response_mime_type="application/json",
                                response_schema=self._cleaned_schema,
                                temperature=0.0,
                            ),
                        ),
                        timeout=35,
                    )
                except Exception as exc:
                    last_error = str(exc)
                    log.warning(
                        "gemini.extract_entities.attempt_failed",
                        model=model_name,
                        error=last_error,
                    )
            log.warning("gemini.extract_entities.giving_up", doc_id=doc_id, error=last_error)
            return None

        try:
            response = await _call_api_with_retry()
            raw = getattr(response, "text", None) if response is not None else None
            if raw:
                parsed = _parse_extraction_response(raw, doc_id)
                if parsed is not None and (parsed.equipment or parsed.failures or parsed.work_orders):
                    log.info("gemini.extract_entities.completed", doc_id=doc_id)
                    return parsed
        except Exception as exc:
            log.warning("gemini.extract_entities.failed", doc_id=doc_id, error=str(exc))

        log.warning("gemini.extract_entities.fallback_to_heuristics", doc_id=doc_id)
        return _fallback_entity_extraction(text, doc_id)

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
You are KITE, an industrial engineering knowledge assistant.

Answer the user's question using ONLY the supplied evidence.

=========================
USER QUERY
=========================

{query}

=========================
DOCUMENT CONTEXT
=========================

{docs_formatted}

=========================
GRAPH CONTEXT
=========================

{graph_formatted}

=========================
RULES
=========================

Use only the supplied evidence.

Do not fabricate facts.

Do not use outside knowledge.

If the answer cannot be determined from the supplied evidence, clearly state:

"The available evidence is insufficient to answer this question."

Prefer graph relationships when they provide stronger evidence.

Mention equipment IDs, work orders, inspections, procedures and regulations exactly as written.

Every factual statement must include an inline citation.

Use:

[Doc X]

for document evidence.

Use:

[Graph]

for graph evidence.

If multiple sources support a statement, cite all of them.

=========================
OUTPUT FORMAT
=========================

Summary

Detailed Explanation

Supporting Evidence

Answer only using the supplied evidence.
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
