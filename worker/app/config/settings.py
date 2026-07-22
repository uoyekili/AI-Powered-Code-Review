"""Application settings loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

WORKER_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Runtime configuration for the review worker."""

    model_config = SettingsConfigDict(
        env_file=WORKER_DIR / ".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )

    # Database
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # Logging
    log_level: str

    # Polling
    poll_interval_seconds: float = 2.0

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

    @field_validator("source_max_file_bytes")
    @classmethod
    def validate_source_max_file_bytes(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("must be positive")
        return value

    @field_validator("source_allowed_extensions", "source_ignored_directories")
    @classmethod
    def validate_source_csv_settings(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("must not be empty")
        return stripped

    @field_validator("poll_interval_seconds")
    @classmethod
    def validate_poll_interval(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("must be positive")
        return value

    @property
    def allowed_exts(self) -> frozenset[str]:
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
        return frozenset(
            value.strip()
            for value in self.source_ignored_directories.split(",")
            if value.strip()
        )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
