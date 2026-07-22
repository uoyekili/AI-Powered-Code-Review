"""Domain types shared by every chunking strategy."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class ChunkingStrategyType(str, Enum):
    """Supported chunking algorithms."""

    SEMANTIC = "semantic"
    RECURSIVE = "recursive"
    TOKEN = "token"
    MARKDOWN = "markdown"
    CODE = "code"
    HYBRID = "hybrid"


@dataclass(frozen=True, slots=True)
class ChunkingOptions:
    """Strategy-independent chunking constraints."""

    strategy: ChunkingStrategyType
    max_size: int
    overlap: int

    def __post_init__(self) -> None:
        if self.max_size <= 0:
            raise ValueError("max_size must be positive")
        if self.overlap < 0:
            raise ValueError("overlap must not be negative")
        if self.overlap >= self.max_size:
            raise ValueError("overlap must be smaller than max_size")


@dataclass(frozen=True, slots=True)
class SourceDocument:
    """A source document before it is split into chunks."""

    path: Path
    content: str
    language: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Chunk:
    """A strategy-produced unit ready for downstream processing."""

    path: str
    content: str
    strategy: ChunkingStrategyType
    start_line: int
    end_line: int
    language: str = "text"
    metadata: Mapping[str, str] = field(default_factory=dict)
