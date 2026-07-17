"""
services/ingestion/resolution_service.py
────────────────────────────────────────
Entity Resolution service to deduplicate variants before graph insertion.
"""
from rapidfuzz import fuzz

from app.infrastructure.logger import log
from app.providers.gemini_provider import GeminiProvider
from app.shared.schemas import ExtractionResult


class ResolutionService:
    def __init__(self):
        self.provider = GeminiProvider()
        self.HIGH_CONFIDENCE_THRESHOLD = 90.0
        self.LLM_ADJUDICATION_THRESHOLD = 75.0

    async def resolve_entities(self, result: ExtractionResult) -> ExtractionResult:
        log.info("resolution_service.started", doc_id=result.doc_id)
        
        resolved_equipment = []
        
        for eq in result.equipment:
            is_merged = False
            for existing in resolved_equipment:
                score = fuzz.ratio(eq.tag_id.lower(), existing.tag_id.lower())
                
                if score >= self.HIGH_CONFIDENCE_THRESHOLD:
                    if eq.tag_id not in existing.aliases and eq.tag_id != existing.tag_id:
                        existing.aliases.append(eq.tag_id)
                    is_merged = True
                    log.info("resolution_service.auto_merged", a=existing.tag_id, b=eq.tag_id, score=score)
                    break
                elif score >= self.LLM_ADJUDICATION_THRESHOLD:
                    decision = await self.provider.adjudicate_entities(
                        candidate_a=existing.tag_id,
                        candidate_b=eq.tag_id,
                        context=f"Equipment Type: {eq.type}"
                    )
                    if decision != "DIFFERENT":
                        if eq.tag_id not in existing.aliases and eq.tag_id != decision:
                            existing.aliases.append(eq.tag_id)
                        if existing.tag_id != decision and existing.tag_id not in existing.aliases:
                            existing.aliases.append(existing.tag_id)
                        existing.tag_id = decision
                        is_merged = True
                        log.info("resolution_service.llm_merged", original=existing.tag_id, new=eq.tag_id, canonical=decision)
                        break
                        
            if not is_merged:
                resolved_equipment.append(eq)
                
        original_count = len(result.equipment)
        result.equipment = resolved_equipment
        resolved_count = len(result.equipment)
        
        log.info(
            "resolution_service.completed", 
            doc_id=result.doc_id, 
            merged=original_count - resolved_count
        )
        return result

resolution_service = ResolutionService()
