"""LLM review interfaces consuming strategy-produced chunks."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain_core.runnables import Runnable

from app.chunking import Chunk, ChunkingOptions, ChunkingService
from app.config.settings import get_settings
from app.schemas.chunk_review_schema import (
    ChunkIssue,
    ChunkReviewResult,
    LLMChunkReviewResponse,
)


class LLMReviewService:
    """Review chunks without depending on a concrete chunking algorithm."""

    def __init__(
        self,
        chunking_service: ChunkingService,
        chunk_review_runnable: Runnable,
    ) -> None:
        self._chunking_service = chunking_service
        self._chunk_review_runnable = chunk_review_runnable

    def chunk_repository(
        self,
        path: Path,
        options: ChunkingOptions,
    ) -> list[Chunk]:
        """
        Delegate repository chunking to the configured application service.

        Args:
            path: Local repository path.
            options: Runtime strategy and size constraints.

        Returns:
            List of code chunks.
        """

        return self._chunking_service.chunk_repository(path, options)

    def review_chunk(self, chunk: Chunk) -> ChunkReviewResult:
        """
        Review one code chunk with an LLM.

        Args:
            chunk: Code chunk to review.

        Returns:
            Chunk review result.
        """

        draft = self._chunk_review_runnable.invoke(self._build_input(chunk))
        return self._to_result(chunk, draft)

    def review_chunks_parallel(
        self,
        chunks: list[Chunk],
    ) -> list[ChunkReviewResult]:
        """
        Review multiple chunks concurrently via the LangChain runnable.

        Result order matches the input ``chunks`` order.

        Args:
            chunks: Code chunks to review.
            max_concurrency: Maximum number of concurrent LLM calls.

        Returns:
            Review results for each chunk.
        """

        settings = get_settings()
        max_concurrency = settings.llm_max_concurrency

        drafts: list[LLMChunkReviewResponse] = self._chunk_review_runnable.batch(
            [self._build_input(chunk) for chunk in chunks],
            config={"max_concurrency": max_concurrency},
        )
        return [
            self._to_result(chunk, draft)
            for chunk, draft in zip(chunks, drafts, strict=True)
        ]

    def _build_input(self, chunk: Chunk) -> dict[str, Any]:
        """
        Build the input for the LLM review runnable.

        Args:
            chunk: Code chunk to review.

        Returns:
            Input for the LLM review runnable.
        """
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
        """
        Convert a LLM draft response to a ChunkReviewResult.

        Args:
            chunk: Code chunk to review.
            draft: LLM draft response.

        Returns:
            Chunk review result.
        """

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
