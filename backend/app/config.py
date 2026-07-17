"""
app/config.py
─────────────
Application configuration via pydantic-settings.
All environment variables are loaded here and typed.

Usage:
    from app.config import settings
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────
    APP_NAME: str       = "KITE"
    APP_ENV: str        = "development"
    APP_VERSION: str    = "0.1.0"
    CORS_ORIGINS: str   = "http://localhost:5173"

    # ── LLM Provider ─────────────────────────────────────────
    LLM_PROVIDER: str          = "gemini"    # gemini | openai | groq | ollama
    GEMINI_API_KEY: str        = ""
    OPENAI_API_KEY: str        = ""
    GROQ_API_KEY: str          = ""
    OLLAMA_BASE_URL: str       = "http://localhost:11434"

    # ── Neo4j ────────────────────────────────────────────────
    NEO4J_URI: str      = "bolt://localhost:7687"
    NEO4J_USER: str     = "neo4j"
    NEO4J_PASSWORD: str = "kite_password"

    # ── Qdrant ───────────────────────────────────────────────
    QDRANT_URL: str         = "http://localhost:6333"
    QDRANT_API_KEY: str     = ""

    # ── PostgreSQL ───────────────────────────────────────────
    DATABASE_URL: str   = "postgresql+asyncpg://kite:kite_password@localhost:5432/kite"

    # ── Embedding & Reranking ────────────────────────────────
    EMBEDDING_MODEL: str    = "BAAI/bge-large-en-v1.5"
    RERANKER_MODEL: str     = "BAAI/bge-reranker-large"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()
