"""Tests for stubbed service interfaces."""

from pathlib import Path

import pytest

from app.chunking import (
    Chunk,
    ChunkingOptions,
    ChunkingStrategyType,
    create_chunking_service,
)
from app.chunking.domain import SourceDocument
from app.schemas.chunk_review_schema import LLMChunkReviewResponse
from app.schemas.review_fixtures import mock_review_result
from app.services.llm_review_service import LLMReviewService
from app.services.report_service import ReportService
from app.services.repository_service import RepositoryService
from app.services.static_analysis_service import StaticAnalysisService


class EmptyDocumentLoader:
    def load(self, root: Path) -> list[SourceDocument]:
        return []


class StubChunkReviewRunnable:
    """Deterministic stand-in for the LangChain chunk-review runnable."""

    def invoke(self, _input: object) -> LLMChunkReviewResponse:
        return LLMChunkReviewResponse(summary="", score=0, issues=[])

    def batch(
        self,
        inputs: list[object],
        config: object | None = None,
    ) -> list[LLMChunkReviewResponse]:
        return [self.invoke(item) for item in inputs]


def test_repository_scan_requires_clone(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        RepositoryService,
        "_load_repository",
        lambda self: type(
            "Repo",
            (),
            {"language": "Python", "get_languages": lambda self: {"Python": 100}},
        )(),
    )
    service = RepositoryService("https://github.com/owner/repo", "main")
    with pytest.raises(RuntimeError, match="must be cloned"):
        service.scan_repository()


def test_static_analysis_returns_empty_result() -> None:
    result = StaticAnalysisService().analyze(Path("."))
    assert result.issues == []


def test_llm_review_returns_empty_chunks() -> None:
    service = LLMReviewService(
        create_chunking_service(loader=EmptyDocumentLoader()),
        StubChunkReviewRunnable(),
    )
    options = ChunkingOptions(
        strategy=ChunkingStrategyType.HYBRID,
        max_size=2_000,
        overlap=200,
    )
    assert service.chunk_repository(Path("."), options) == []
    chunk = Chunk(
        path="main.py",
        content="print('hi')",
        strategy=ChunkingStrategyType.CODE,
        start_line=1,
        end_line=1,
    )
    assert service.review_chunk(chunk).score == 0
    assert service.review_chunks_parallel([chunk])[0].file_path == "main.py"
    assert service.review_chunks_parallel([]) == []


def test_report_service_generates_markdown() -> None:
    review = mock_review_result(
        task_id="abc",
        repository_url="https://github.com/owner/repo",
        branch="main",
        owner="owner",
        name="repo",
    )
    markdown = ReportService().generate_markdown(review)
    assert "Code Review Report" in markdown
    assert "https://github.com/owner/repo" in markdown
