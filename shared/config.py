"""
Shared Configuration for CrisisBridge AI
==========================================
Centralized settings loaded from environment variables.
Used by ALL team members. DO NOT duplicate config in your modules.

Usage:
    from shared.config import settings
    print(settings.DATABASE_URL)
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application-wide settings.
    Values are loaded from .env file or environment variables.
    """

    # ── App ──────────────────────────────────────
    APP_NAME: str = "CrisisBridge AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "change-this-in-production-use-a-real-secret"
    API_PREFIX: str = "/api/v1"

    # ── Auth (JWT) ───────────────────────────────
    JWT_SECRET_KEY: str = "jwt-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ── Database (SQLite default for local dev) ──────
    DATABASE_URL: str = "sqlite:///./crisisbridge.db"
    DB_ECHO: bool = False  # Set True to print SQL queries (debug)

    # ── Redis ────────────────────────────────────
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    CACHE_TTL_SECONDS: int = 300  # 5 minutes default cache TTL

    # ── FAISS / Vector DB ────────────────────────
    FAISS_INDEX_PATH: str = "data/faiss_index"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # sentence-transformers model
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K_RESULTS: int = 5

    # ── AI / LLM ─────────────────────────────────
    LLM_MODEL: str = "gpt-3.5-turbo"  # or local model path
    LLM_API_KEY: Optional[str] = None
    LLM_BASE_URL: Optional[str] = None  # For local LLM endpoints
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 1024

    # ── Session Memory ───────────────────────────
    SESSION_MEMORY_SIZE: int = 5  # Last N queries to remember

    # ── Safety System ────────────────────────────
    SAFETY_RADIUS_WARNING_METERS: float = 100.0  # Warning zone radius
    SAFETY_RADIUS_EVACUATE_METERS: float = 50.0  # Evacuation zone radius

    # ── Logging ──────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/crisisbridge.log"

    # ── CORS ─────────────────────────────────────
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Singleton settings instance — import this everywhere
settings = Settings()
