"""Tests for chunking architecture boundaries and orchestration."""

from collections.abc import Sequence
from pathlib import Path

import pytest

from app.chunking import Chunk, ChunkingOptions, ChunkingStrategyType, SourceDocument
from app.chunking.registry import ChunkingStrategyRegistry, StrategyNotRegisteredError
from app.chunking.service import ChunkingService


class StubDocumentLoader:
    def __init__(self, documents: Sequence[SourceDocument]) -> None:
        self.documents = documents

    def load(self, root: Path) -> Sequence[SourceDocument]:
        return self.documents


class StubCodeStrategy:
    strategy_type = ChunkingStrategyType.CODE

    def supports(self, document: SourceDocument) -> bool:
        return document.path.suffix == ".py"

    def chunk(
        self,
        document: SourceDocument,
        options: ChunkingOptions,
    ) -> Sequence[Chunk]:
        return [
            Chunk(
                path=str(document.path),
                content=document.content,
                strategy=self.strategy_type,
                start_line=1,
                end_line=1,
            )
        ]


def test_chunking_service_uses_injected_loader_and_strategy() -> None:
    loader = StubDocumentLoader(
        [
            SourceDocument(path=Path("main.py"), content="print('hello')"),
            SourceDocument(path=Path("README.md"), content="# Demo"),
        ]
    )
    registry = ChunkingStrategyRegistry([StubCodeStrategy()])
    service = ChunkingService(loader, registry)

    chunks = service.chunk_repository(
        Path("/repo"),
        ChunkingOptions(
            strategy=ChunkingStrategyType.CODE,
            max_size=2_000,
            overlap=200,
        ),
    )

    assert [chunk.path for chunk in chunks] == ["main.py"]


def test_registry_reports_unregistered_strategy() -> None:
    registry = ChunkingStrategyRegistry()

    with pytest.raises(StrategyNotRegisteredError):
        registry.get(ChunkingStrategyType.SEMANTIC)


def test_chunking_options_reject_invalid_overlap() -> None:
    with pytest.raises(ValueError):
        ChunkingOptions(
            strategy=ChunkingStrategyType.HYBRID,
            max_size=100,
            overlap=100,
        )
