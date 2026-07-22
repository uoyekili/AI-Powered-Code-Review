"""Prompt template for single-chunk code review."""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

CHUNK_REVIEW_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a senior code reviewer. "
            "Find concrete issues in the given chunk only. "
            "Use type in: security, performance, maintainability, "
            "code-quality, architecture. "
            "Use severity in: critical, high, medium, low, info. "
            "Prefer absolute file line numbers.",
        ),
        (
            "human",
            "File: {file_path}\n"
            "Lines: {start_line}-{end_line}\n\n"
            "```{language}\n{content}\n```",
        ),
    ]
)
