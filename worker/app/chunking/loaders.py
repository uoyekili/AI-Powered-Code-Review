"""Document-loader adapters for chunking application services."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from app.chunking.domain import SourceDocument


@dataclass(frozen=True, slots=True)
class FileSystemLoaderOptions:
    """Safety limits for repository document discovery."""

    max_file_bytes: int
    allowed_extensions: frozenset[str]
    ignored_directories: frozenset[str]

    def __post_init__(self) -> None:
        if self.max_file_bytes <= 0:
            raise ValueError("max_file_bytes must be positive")
        if not self.allowed_extensions:
            raise ValueError("allowed_extensions must not be empty")
        if any(not extension.startswith(".") for extension in self.allowed_extensions):
            raise ValueError("allowed_extensions must include leading dots")


class FileSystemDocumentLoader:
    """Load text documents from a local repository."""

    def __init__(self, options: FileSystemLoaderOptions) -> None:
        self._options = options

    def load(self, root: Path) -> Sequence[SourceDocument]:
        # TODO: Discover safe text files, enforce limits, and detect languages.
        return []
