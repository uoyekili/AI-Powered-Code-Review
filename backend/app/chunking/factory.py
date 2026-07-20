"""Composition root for the chunking subsystem."""

from __future__ import annotations

from app.chunking.loaders import FileSystemDocumentLoader, FileSystemLoaderOptions
from app.chunking.ports import DocumentLoader, EmbeddingProvider, TokenCounter
from app.chunking.registry import ChunkingStrategyRegistry
from app.chunking.service import ChunkingService
from app.chunking.strategies import (
    CodeChunkingStrategy,
    HybridChunkingStrategy,
    MarkdownChunkingStrategy,
    RecursiveChunkingStrategy,
    SemanticChunkingStrategy,
    TokenChunkingStrategy,
)
from app.config.settings import get_settings


def create_chunking_service(*, loader: DocumentLoader) -> ChunkingService:
    """
    Build the MVP strategy graph.

    Registers Markdown, Code, Recursive, and Hybrid. Token and Semantic
    strategies are omitted until their required infrastructure is supplied.
    """

    recursive = RecursiveChunkingStrategy()
    markdown = MarkdownChunkingStrategy()
    code = CodeChunkingStrategy()
    hybrid = HybridChunkingStrategy(
        strategies=(markdown, code),
        fallback=recursive,
    )
    registry = ChunkingStrategyRegistry((recursive, markdown, code, hybrid))
    return ChunkingService(loader=loader, registry=registry)


def create_token_aware_chunking_service(
    *,
    loader: DocumentLoader,
    token_counter: TokenCounter,
) -> ChunkingService:
    """Build the MVP graph plus a Token strategy that requires a counter."""

    recursive = RecursiveChunkingStrategy()
    token = TokenChunkingStrategy(token_counter)
    markdown = MarkdownChunkingStrategy()
    code = CodeChunkingStrategy()
    hybrid = HybridChunkingStrategy(
        strategies=(markdown, code),
        fallback=recursive,
    )
    registry = ChunkingStrategyRegistry((recursive, token, markdown, code, hybrid))
    return ChunkingService(loader=loader, registry=registry)


def create_semantic_chunking_service(
    *,
    loader: DocumentLoader,
    embedding_provider: EmbeddingProvider,
) -> ChunkingService:
    """Build the MVP graph plus a Semantic strategy that requires embeddings."""

    recursive = RecursiveChunkingStrategy()
    semantic = SemanticChunkingStrategy(embedding_provider)
    markdown = MarkdownChunkingStrategy()
    code = CodeChunkingStrategy()
    hybrid = HybridChunkingStrategy(
        strategies=(markdown, code),
        fallback=recursive,
    )
    registry = ChunkingStrategyRegistry((semantic, recursive, markdown, code, hybrid))
    return ChunkingService(loader=loader, registry=registry)


def create_default_chunking_service() -> ChunkingService:
    """Create the production MVP chunking service from application settings."""

    settings = get_settings()
    loader = FileSystemDocumentLoader(
        FileSystemLoaderOptions(
            max_file_bytes=settings.source_max_file_bytes,
            allowed_extensions=settings.allowed_exts,
            ignored_directories=settings.ignored_dirs,
        )
    )
    return create_chunking_service(loader=loader)
