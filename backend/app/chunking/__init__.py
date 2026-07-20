"""Public API for the chunking subsystem."""

from app.chunking.domain import (
    Chunk,
    ChunkingOptions,
    ChunkingStrategyType,
    SourceDocument,
)
from app.chunking.factory import (
    create_chunking_service,
    create_default_chunking_service,
    create_semantic_chunking_service,
    create_token_aware_chunking_service,
)
from app.chunking.service import ChunkingService

__all__ = [
    "Chunk",
    "ChunkingOptions",
    "ChunkingService",
    "ChunkingStrategyType",
    "SourceDocument",
    "create_chunking_service",
    "create_default_chunking_service",
    "create_semantic_chunking_service",
    "create_token_aware_chunking_service",
]
