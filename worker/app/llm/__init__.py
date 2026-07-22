"""Optional LLM integration (requires langchain packages when used)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langchain_core.runnables import Runnable

__all__ = ["create_chunk_review_runnable"]


def create_chunk_review_runnable() -> Runnable:
    from app.llm.runnables.chunk_review import (
        create_chunk_review_runnable as _create_chunk_review_runnable,
    )

    return _create_chunk_review_runnable()
