"""Application service orchestrating loading and chunking."""

from __future__ import annotations

from pathlib import Path

from app.chunking.domain import Chunk, ChunkingOptions, SourceDocument
from app.chunking.ports import DocumentLoader
from app.chunking.registry import ChunkingStrategyRegistry


class ChunkingService:
    """Coordinate document loading and runtime strategy selection."""

    def __init__(
        self,
        loader: DocumentLoader,
        registry: ChunkingStrategyRegistry,
    ) -> None:
        self._loader = loader
        self._registry = registry

    def chunk_repository(
        self,
        root: Path,
        options: ChunkingOptions,
    ) -> list[Chunk]:
        """Load and chunk every supported document in a repository."""

        chunks: list[Chunk] = []
        for document in self._loader.load(root):
            chunks.extend(self.chunk_document(document, options))
        return chunks

    def chunk_document(
        self,
        document: SourceDocument,
        options: ChunkingOptions,
    ) -> list[Chunk]:
        """Chunk one document using the requested strategy."""

        strategy = self._registry.get(options.strategy)
        if not strategy.supports(document):
            return []
        return list(strategy.chunk(document, options))
