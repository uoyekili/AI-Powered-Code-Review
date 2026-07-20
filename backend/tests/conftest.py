"""Shared pytest fixtures."""

from __future__ import annotations

import os

# Settings are loaded at import time by the database session module.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/code_review",
)
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")
