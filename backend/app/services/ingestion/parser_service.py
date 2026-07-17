"""
services/ingestion/parser_service.py
────────────────────────────────────
Docling wrapper for document parsing.
"""
from pathlib import Path

from docling.document_converter import DocumentConverter

from app.infrastructure.logger import log


class ParserService:
    def __init__(self):
        self._converter = None

    @property
    def converter(self):
        # Lazy load because initialization can be heavy
        if self._converter is None:
            log.info("parser_service.initializing")
            self._converter = DocumentConverter()
            log.info("parser_service.initialized")
        return self._converter

    def parse_document(self, file_path: Path) -> str:
        """Parse a document into markdown representation using Docling."""
        log.info("parser_service.converting", file_path=str(file_path))
        result = self.converter.convert(file_path)
        md_text = result.document.export_to_markdown()
        log.info("parser_service.converted", file_path=str(file_path), md_length=len(md_text))
        return md_text

parser_service = ParserService()
