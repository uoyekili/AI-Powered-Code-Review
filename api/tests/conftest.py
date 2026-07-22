"""Shared pytest fixtures."""

from __future__ import annotations

import os

os.environ.setdefault("POSTGRES_USER", "postgres")
os.environ.setdefault("POSTGRES_PASSWORD", "postgres")
os.environ.setdefault("POSTGRES_DB", "code_review")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("API_PREFIX", "/api")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")
os.environ.setdefault("LOG_LEVEL", "INFO")
