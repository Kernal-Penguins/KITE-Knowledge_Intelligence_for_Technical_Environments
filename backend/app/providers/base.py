"""
providers/base.py
─────────────────
Abstract Base Class for LLM Providers.
"""
from abc import ABC, abstractmethod

from app.shared.schemas import ExtractionResult


class LLMProvider(ABC):
    @abstractmethod
    async def extract_entities(self, text: str, doc_id: str) -> ExtractionResult:
        """Extract structured entities from a document chunk."""
        pass

    @abstractmethod
    async def adjudicate_entities(self, candidate_a: str, candidate_b: str, context: str) -> str:
        """Adjudicate between two similar entities for resolution."""
        pass

    @abstractmethod
    async def generate_answer(self, query: str, context: list[str], citations: list) -> str:
        """Generate a user-facing answer using hybrid search context."""
        pass

    @abstractmethod
    async def generate_rca_report(self, equipment_id: str, failure_chain: list) -> str:
        """Generate a Root Cause Analysis report for a piece of equipment."""
        pass
