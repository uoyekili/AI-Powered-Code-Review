"""Ports implemented by chunking infrastructure and strategies."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from app.chunking.domain import (
    Chunk,
    ChunkingOptions,
    ChunkingStrategyType,
    SourceDocument,
)


class DocumentLoader(Protocol):
    """Load source documents without coupling chunking to a filesystem."""

    def load(self, root: Path) -> Sequence[SourceDocument]:
        """Return documents found under the supplied root."""


class ChunkingStrategy(Protocol):
    """Strategy contract used by the chunking application service."""

    @property
    def strategy_type(self) -> ChunkingStrategyType:
        """Return the unique strategy identifier."""

    def supports(self, document: SourceDocument) -> bool:
        """Return whether this strategy can process the document."""

    def chunk(
        self,
        document: SourceDocument,
        options: ChunkingOptions,
    ) -> Sequence[Chunk]:
        """Split one document into chunks."""


class TokenCounter(Protocol):
    """Count model-specific tokens without coupling to an SDK."""

    def count(self, text: str) -> int:
        """Return the token count for text."""


class EmbeddingProvider(Protocol):
    """Generate embeddings without coupling semantic chunking to an SDK."""

    def embed(self, texts: Sequence[str]) -> Sequence[Sequence[float]]:
        """Return one embedding per input text."""
