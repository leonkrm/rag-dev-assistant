"""
Централизованная конфигурация приложения.
Значения читаются из переменных окружения (см. .env в корне backend/).
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Общие ---
    APP_NAME: str = "RAG Dev Assistant"
    ENV: str = "local"
    LOG_LEVEL: str = "INFO"

    # --- База данных ---
    DATABASE_URL: str = "postgresql+asyncpg://rag:rag@localhost:5432/rag"

    # --- Эмбеддинги ---
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384

    # --- LLM ---
    LLM_PROVIDER: str = "anthropic"
    LLM_MODEL: str = "claude-sonnet-4-6"
    LLM_API_KEY: str = "YOUR_LLM_API_KEY"
    LLM_API_BASE_URL: str = "https://api.anthropic.com/v1/messages"
    LLM_MAX_TOKENS: int = 1024

    # --- RAG ---
    RAG_TOP_K: int = 5
    RAG_CHUNK_SIZE: int = 800
    RAG_CHUNK_OVERLAP: int = 150


@lru_cache
def get_settings() -> Settings:
    return Settings()
