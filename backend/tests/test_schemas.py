"""Tests for schema mock factories."""

from app.schemas.review_schema import empty_metrics, mock_review_result


def test_empty_metrics_are_zero() -> None:
    metrics = empty_metrics()
    assert metrics.overall_score == 0
    assert metrics.security_score == 0


def test_mock_review_result() -> None:
    review = mock_review_result(
        task_id="abc",
        repository_url="https://github.com/owner/repo",
        branch="main",
        owner="owner",
        name="repo",
    )
    assert review.id == "abc"
    assert review.repository.owner == "owner"
    assert review.branch == "main"
    assert review.files == []
    assert review.progress == 100
