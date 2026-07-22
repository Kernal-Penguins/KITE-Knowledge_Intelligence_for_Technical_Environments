"""
tests/conftest.py
──────────────────
Shared pytest configuration for the KITE test suite.

Patches heavy ML libraries at the module level so that unit tests can
collect and run without downloading / initialising sentence-transformers,
docling, or Google genai clients.

These patches are automatically applied to every test session.
Integration tests that need real clients should be run separately
against a live stack (see tests/integration/).
"""
import sys
from unittest.mock import MagicMock, patch

# ── Stub out heavy ML libraries before any app module is imported ──────────
# This prevents test collection from hanging while sentence-transformers
# downloads models or docling initialises its pipeline.

_HEAVY_MODULES = [
    "docling",
    "docling.document_converter",
    "sentence_transformers",
    "FlagEmbedding",
    "torch",
    "transformers",
    "google.generativeai",
    "google.genai",
]

for _mod in _HEAVY_MODULES:
    if _mod not in sys.modules:
        sys.modules[_mod] = MagicMock()
