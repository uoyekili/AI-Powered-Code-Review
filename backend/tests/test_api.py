"""API route tests using dependency overrides."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.schemas.review_schema import (
    AnalysisStepSchema,
    ProgressResponse,
    SubmitReviewResponse,
    mock_review_result,
)


class FakeReviewService:
    """In-memory stand-in for ReviewService."""

    async def submit_review(self, repository_url: str, branch: str) -> str:
        assert "github.com" in repository_url
        assert branch == "develop"
        return "11111111-1111-1111-1111-111111111111"

    async def get_review(self, task_id: str):
        return mock_review_result(
            task_id=task_id,
            repository_url="https://github.com/owner/repo",
            branch="develop",
            owner="owner",
            name="repo",
        )

    async def get_progress(self, task_id: str) -> ProgressResponse:
        return ProgressResponse(
            progress=50,
            current_step="Static Analysis",
            status="in-progress",
            steps=[
                AnalysisStepSchema(
                    id="static",
                    name="Static Analysis",
                    description="Run checks",
                    status="in-progress",
                    estimated_time=40,
                )
            ],
        )

    async def get_report(self, task_id: str) -> str:
        return f"# Report for {task_id}\n"


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    fake = FakeReviewService()

    from app.api.dependencies import get_review_service

    app.dependency_overrides[get_review_service] = lambda: fake

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_submit_review(client: TestClient) -> None:
    response = client.post(
        "/api/review",
        json={
            "repositoryUrl": "https://github.com/owner/repo",
            "branch": "develop",
        },
    )
    assert response.status_code == 200
    payload = SubmitReviewResponse.model_validate(response.json())
    assert payload.review_id == "11111111-1111-1111-1111-111111111111"


def test_submit_review_requires_branch(client: TestClient) -> None:
    response = client.post(
        "/api/review",
        json={"repositoryUrl": "https://github.com/owner/repo"},
    )

    assert response.status_code == 422


def test_get_progress(client: TestClient) -> None:
    response = client.get("/api/review/11111111-1111-1111-1111-111111111111/progress")
    assert response.status_code == 200
    assert response.json()["progress"] == 50
    assert response.json()["currentStep"] == "Static Analysis"


def test_get_review(client: TestClient) -> None:
    response = client.get("/api/review/11111111-1111-1111-1111-111111111111")
    assert response.status_code == 200
    body = response.json()
    assert body["repository"]["owner"] == "owner"
    assert body["metrics"]["overallScore"] == 0


def test_get_report(client: TestClient) -> None:
    response = client.get("/api/report/11111111-1111-1111-1111-111111111111")
    assert response.status_code == 200
    assert "Report for" in response.text
