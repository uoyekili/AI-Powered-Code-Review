"""Extensible chunking strategy skeletons.

Only capability routing and dependency boundaries live here. The splitting
algorithms are intentionally left as TODOs for incremental implementation.
"""

from __future__ import annotations

from collections.abc import Sequence

from app.chunking.domain import (
    Chunk,
    ChunkingOptions,
    ChunkingStrategyType,
    SourceDocument,
)
from app.chunking.ports import ChunkingStrategy, EmbeddingProvider, TokenCounter


class RecursiveChunkingStrategy:
    """Recursively split text using an ordered separator hierarchy."""

    strategy_type = ChunkingStrategyType.RECURSIVE

    def supports(self, document: SourceDocument) -> bool:
        return True

    def chunk(
        self,
        document: SourceDocument,
        options: ChunkingOptions,
    ) -> Sequence[Chunk]:
        # TODO: Recursively split by semantic separators until max_size is met.
        return []


class TokenChunkingStrategy:
    """Split documents according to model-specific token counts."""

    strategy_type = ChunkingStrategyType.TOKEN

    def __init__(self, token_counter: TokenCounter) -> None:
        self._token_counter = token_counter

    def supports(self, document: SourceDocument) -> bool:
        return True

    def chunk(
        self,
        document: SourceDocument,
        options: ChunkingOptions,
    ) -> Sequence[Chunk]:
        # TODO: Split on max_size token boundaries using self._token_counter.
        return []


class SemanticChunkingStrategy:
    """Split text where adjacent semantic similarity falls below a threshold."""

    strategy_type = ChunkingStrategyType.SEMANTIC

    def __init__(self, embedding_provider: EmbeddingProvider) -> None:
        self._embedding_provider = embedding_provider

    def supports(self, document: SourceDocument) -> bool:
        return True

    def chunk(
        self,
        document: SourceDocument,
        options: ChunkingOptions,
    ) -> Sequence[Chunk]:
        # TODO: Detect semantic boundaries using self._embedding_provider.
        return []


class MarkdownChunkingStrategy:
    """Split Markdown while preserving heading hierarchy and fenced blocks."""

    strategy_type = ChunkingStrategyType.MARKDOWN

    def supports(self, document: SourceDocument) -> bool:
        return document.path.suffix.lower() in {".md", ".mdx"}

    def chunk(
        self,
        document: SourceDocument,
        options: ChunkingOptions,
    ) -> Sequence[Chunk]:
        # TODO: Build chunks from headings without splitting fenced code blocks.
        return []


class CodeChunkingStrategy:
    """Split source code on language-aware structural boundaries."""

    strategy_type = ChunkingStrategyType.CODE
    _supported_suffixes = frozenset(
        {
            ".c",
            ".cpp",
            ".cs",
            ".go",
            ".java",
            ".js",
            ".jsx",
            ".kt",
            ".php",
            ".py",
            ".rb",
            ".rs",
            ".swift",
            ".ts",
            ".tsx",
        }
    )

    def supports(self, document: SourceDocument) -> bool:
        return document.path.suffix.lower() in self._supported_suffixes

    def chunk(
        self,
        document: SourceDocument,
        options: ChunkingOptions,
    ) -> Sequence[Chunk]:
        # TODO: Parse language syntax and split on module/class/function boundaries.
        return []


class HybridChunkingStrategy:
    """Compose specialized strategies and apply a configurable fallback."""

    strategy_type = ChunkingStrategyType.HYBRID

    def __init__(
        self,
        strategies: Sequence[ChunkingStrategy],
        fallback: ChunkingStrategy,
    ) -> None:
        self._strategies = tuple(strategies)
        self._fallback = fallback

    def supports(self, document: SourceDocument) -> bool:
        return True

    def chunk(
        self,
        document: SourceDocument,
        options: ChunkingOptions,
    ) -> Sequence[Chunk]:
        # TODO: Select a specialized strategy, then enforce token-size constraints.
        strategy = next(
            (
                candidate
                for candidate in self._strategies
                if candidate.supports(document)
            ),
            self._fallback,
        )
        delegated_options = ChunkingOptions(
            strategy=strategy.strategy_type,
            max_size=options.max_size,
            overlap=options.overlap,
        )
        return strategy.chunk(document, delegated_options)
