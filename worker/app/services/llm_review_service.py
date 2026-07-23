"""LLM review interfaces consuming strategy-produced chunks."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from app.chunking import Chunk, ChunkingOptions, ChunkingService
from app.config.settings import get_settings
from app.schemas.chunk_review_schema import (
    ChunkIssue,
    ChunkReviewResult,
    LLMChunkReviewResponse,
)


class ChunkReviewRunnable(Protocol):
    """Minimal contract for a LangChain-style chunk review runnable."""

    def invoke(self, input: dict[str, Any]) -> LLMChunkReviewResponse: ...

    def batch(
        self,
        inputs: list[dict[str, Any]],
        config: dict[str, Any] | None = None,
    ) -> list[LLMChunkReviewResponse]: ...


class LLMReviewService:
    """Review chunks without depending on a concrete chunking algorithm."""

    def __init__(
        self,
        chunking_service: ChunkingService,
        chunk_review_runnable: ChunkReviewRunnable,
    ) -> None:
        self._chunking_service = chunking_service
        self._chunk_review_runnable = chunk_review_runnable

    def chunk_repository(
        self,
        path: Path,
        options: ChunkingOptions,
    ) -> list[Chunk]:
        return self._chunking_service.chunk_repository(path, options)

    def review_chunk(self, chunk: Chunk) -> ChunkReviewResult:
        draft = self._chunk_review_runnable.invoke(self._build_input(chunk))
        return self._to_result(chunk, draft)

    def review_chunks_parallel(
        self,
        chunks: list[Chunk],
    ) -> list[ChunkReviewResult]:
        settings = get_settings()
        max_concurrency = settings.llm_max_concurrency

        drafts: list[LLMChunkReviewResponse] = self._chunk_review_runnable.batch(
            [self._build_input(chunk) for chunk in chunks],
            config={"max_concurrency": max_concurrency},
        )
        return [self._to_result(chunk, draft) for chunk, draft in zip(chunks, drafts, strict=True)]

    def _build_input(self, chunk: Chunk) -> dict[str, Any]:
        return {
            "file_path": chunk.path,
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
            "language": chunk.language,
            "content": chunk.content,
        }

    def _to_result(
        self,
        chunk: Chunk,
        draft: LLMChunkReviewResponse,
    ) -> ChunkReviewResult:
        issues: list[ChunkIssue] = []
        for index, item in enumerate(draft.issues):
            line = min(max(item.line, chunk.start_line), chunk.end_line)
            issues.append(
                ChunkIssue(
                    id=f"{chunk.path}:{line}:{index}",
                    file=chunk.path,
                    line=line,
                    type=item.type,
                    severity=item.severity,
                    title=item.title,
                    description=item.description,
                    suggestion=item.suggestion,
                    code=item.code,
                )
            )

        return ChunkReviewResult(
            file_path=chunk.path,
            summary=draft.summary,
            score=draft.score,
            issues=issues,
        )
