"""Application settings loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

API_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Runtime configuration for the public API."""

    model_config = SettingsConfigDict(
        env_file=API_DIR / ".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )

    # Database
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # API / CORS
    api_prefix: str
    cors_origins: str

    # Logging
    log_level: str

    @field_validator("cors_origins")
    @classmethod
    def strip_required_strings(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("must not be empty")
        return stripped

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
