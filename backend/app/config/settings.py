"""Application settings loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Root of the backend folder
BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Runtime configuration for the API skeleton."""

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )

    # Database
    postgres_user: str
    postgres_password: str
    postgres_db: str

    # API / CORS
    api_prefix: str
    cors_origins: str

    # Logging
    log_level: str

    # Azure OpenAI
    azure_openai_base_url: str
    azure_openai_chat_api_key: str
    azure_openai_chat_model: str

    # LLM Review
    llm_max_concurrency: int

    # Repository
    clone_dir: str

    # Source discovery
    source_max_file_bytes: int
    source_allowed_extensions: str
    source_ignored_directories: str

    # Validators
    @field_validator("cors_origins")
    @classmethod
    def strip_required_strings(cls, value: str) -> str:
        """Trim whitespace and reject empty values."""
        stripped = value.strip()
        if not stripped:
            raise ValueError("must not be empty")
        return stripped

    @field_validator("source_max_file_bytes")
    @classmethod
    def validate_source_max_file_bytes(cls, value: int) -> int:
        """Require a positive per-file loading limit."""
        if value <= 0:
            raise ValueError("must be positive")
        return value

    @field_validator("source_allowed_extensions", "source_ignored_directories")
    @classmethod
    def validate_source_csv_settings(cls, value: str) -> str:
        """Reject empty comma-separated source discovery settings."""
        stripped = value.strip()
        if not stripped:
            raise ValueError("must not be empty")
        return stripped

    # Derived properties
    @property
    def cors_origin_list(self) -> list[str]:
        """Split cors_origins into a clean list of origins."""
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]

    @property
    def allowed_exts(self) -> frozenset[str]:
        """Normalized extensions accepted for processing."""
        return frozenset(
            extension if extension.startswith(".") else f".{extension}"
            for extension in (
                value.strip().lower()
                for value in self.source_allowed_extensions.split(",")
                if value.strip()
            )
        )

    @property
    def ignored_dirs(self) -> frozenset[str]:
        """Directory names excluded from repository discovery."""
        return frozenset(
            value.strip()
            for value in self.source_ignored_directories.split(",")
            if value.strip()
        )

    @property
    def database_url(self) -> str:
        """Build the PostgreSQL connection string (asyncpg driver)."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@localhost:5432/{self.postgres_db}"
        )


# Cached so the .env file is only read once
@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings instance."""
    return Settings()
