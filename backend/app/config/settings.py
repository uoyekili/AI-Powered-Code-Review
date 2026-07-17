from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Application settings loaded from environment variables and backend/.env."""

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Required
    database_url: str
    cors_origins: str
    azure_openai_base_url: str
    azure_openai_chat_api_key: str
    azure_openai_chat_model: str
    azure_openai_embedding_api_key: str
    azure_openai_embedding_model: str
    clone_dir: str


    # Optional
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO"
    )
    api_prefix: str = Field(default="/api")
    max_files_to_review: int = Field(default=15, ge=1)
    max_file_size_bytes: int = Field(default=50_000, ge=1)
    max_total_chars: int = Field(default=120_000, ge=1)
    chunk_size_chars: int = Field(default=12_000, ge=1)

    @field_validator("database_url", "cors_origins", "azure_openai_base_url")
    @classmethod
    def strip_required_strings(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("must not be empty")
        return stripped

    @field_validator(
        "azure_openai_chat_api_key",
        "azure_openai_chat_model",
        "azure_openai_embedding_api_key",
        "azure_openai_embedding_model",
    )
    @classmethod
    def strip_required_secrets(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("must not be empty")
        return stripped

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
