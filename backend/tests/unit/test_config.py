"""
tests/unit/test_config.py
──────────────────────────
Unit tests for app/config.py — validates the Settings class
loads defaults correctly without any .env file required.
"""
import pytest

from app.config import Settings


class TestSettings:
    def test_defaults_are_sensible(self):
        s = Settings()
        assert s.APP_NAME == "KITE"
        assert s.APP_ENV == "development"
        assert s.APP_VERSION == "0.1.0"

    def test_is_production_false_by_default(self):
        s = Settings()
        assert s.is_production is False

    def test_is_production_true_when_env_set(self):
        s = Settings(APP_ENV="production")
        assert s.is_production is True

    def test_cors_origins_list_single(self):
        s = Settings(CORS_ORIGINS="http://localhost:5173")
        assert s.cors_origins_list == ["http://localhost:5173"]

    def test_cors_origins_list_multiple(self):
        s = Settings(CORS_ORIGINS="http://localhost:5173,https://app.example.com")
        assert len(s.cors_origins_list) == 2
        assert "https://app.example.com" in s.cors_origins_list

    def test_cors_origins_list_strips_whitespace(self):
        s = Settings(CORS_ORIGINS="  http://localhost:5173 , https://example.com  ")
        origins = s.cors_origins_list
        assert all(o == o.strip() for o in origins)

    def test_default_neo4j_uri(self):
        s = Settings()
        assert "7687" in s.NEO4J_URI  # bolt port

    def test_default_qdrant_url(self):
        s = Settings()
        assert "6333" in s.QDRANT_URL

    def test_gemini_api_key_is_a_string(self):
        """GEMINI_API_KEY should always be a string (may be populated from .env)."""
        s = Settings()
        assert isinstance(s.GEMINI_API_KEY, str)
