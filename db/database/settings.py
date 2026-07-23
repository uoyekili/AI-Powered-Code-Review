"""Postgres connection settings for Alembic and shared callers."""

from __future__ import annotations

import os
from collections.abc import Mapping
from functools import lru_cache
from typing import Self

from pydantic import BaseModel, Field


class DatabaseSettings(BaseModel):
    """Immutable Postgres settings built from an explicit environ mapping."""

    postgres_user: str = Field(init=False)
    postgres_password: str = Field(init=False)
    postgres_db: str = Field(init=False)
    postgres_host: str = Field(init=False)
    postgres_port: int = Field(init=False, ge=1, le=65535)

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def sync_database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_database_settings() -> DatabaseSettings:
    """Cached settings loaded from the current process environment."""

    return DatabaseSettings()
