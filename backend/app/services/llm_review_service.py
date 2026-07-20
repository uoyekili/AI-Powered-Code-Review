"""LLM review interfaces consuming strategy-produced chunks."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.chunking import Chunk, ChunkingOptions, ChunkingService


@dataclass(frozen=True, slots=True)
class ChunkReviewResult:
    """Review findings for a single code chunk."""

    chunk_path: str
    issues: list[dict[str, object]] = field(default_factory=list)
    summary: str = ""
    score: int = 0


class LLMReviewService:
    """Review chunks without depending on a concrete chunking algorithm."""

    def __init__(self, chunking_service: ChunkingService) -> None:
        self._chunking_service = chunking_service

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

        TODO:
            Implement LLM review for a single chunk.
        """

        return ChunkReviewResult(chunk_path=chunk.path)

    def review_chunks_parallel(self, chunks: list[Chunk]) -> list[ChunkReviewResult]:
        """
        Review multiple chunks in parallel.

        Args:
            chunks: Code chunks to review.

        Returns:
            Review results for each chunk.

        TODO:
            Implement parallel LLM workers.
        """

        return [self.review_chunk(chunk) for chunk in chunks]
