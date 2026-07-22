"""Shared pytest fixtures."""

from __future__ import annotations

import os

os.environ.setdefault("POSTGRES_USER", "postgres")
os.environ.setdefault("POSTGRES_PASSWORD", "postgres")
os.environ.setdefault("POSTGRES_DB", "code_review")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("LOG_LEVEL", "INFO")
os.environ.setdefault("POLL_INTERVAL_SECONDS", "2")
os.environ.setdefault("CLONE_DIR", "/tmp/repos")
os.environ.setdefault("SOURCE_MAX_FILE_BYTES", "1000000")
os.environ.setdefault("SOURCE_ALLOWED_EXTENSIONS", ".py,.tsx")
os.environ.setdefault(
    "SOURCE_IGNORED_DIRECTORIES",
    ".git,.venv,__pycache__,node_modules,.next,build,dist,vendor",
)
os.environ.setdefault("AZURE_OPENAI_BASE_URL", "https://example.openai.azure.com")
os.environ.setdefault("AZURE_OPENAI_CHAT_API_KEY", "test-key")
os.environ.setdefault("AZURE_OPENAI_CHAT_MODEL", "gpt-test")
os.environ.setdefault("LLM_MAX_CONCURRENCY", "2")
