"""Factory helpers for empty and mock review payloads."""

from __future__ import annotations

from app.schemas.review_response import (
    CodeReviewMetricsSchema,
    IssueSeveritySchema,
    IssuesByCategorySchema,
    RepositorySchema,
    ReviewSchema,
)


def empty_metrics() -> CodeReviewMetricsSchema:
    """Return zeroed metric scores."""

    return CodeReviewMetricsSchema(
        overall_score=0,
        security_score=0,
        performance_score=0,
        maintainability_score=0,
        code_quality_score=0,
        architecture_score=0,
    )


def empty_severity() -> IssueSeveritySchema:
    """Return zeroed severity counts."""

    return IssueSeveritySchema(
        critical=0,
        high=0,
        medium=0,
        low=0,
        info=0,
    )


def empty_categories() -> IssuesByCategorySchema:
    """Return zeroed category counts."""

    return IssuesByCategorySchema(
        security=0,
        performance=0,
        maintainability=0,
        code_quality=0,
        architecture=0,
    )


def mock_repository(owner: str, name: str, url: str) -> RepositorySchema:
    """
    Build a placeholder repository summary.

    Args:
        owner: GitHub owner name.
        name: Repository name.
        url: Canonical repository URL.

    Returns:
        Repository schema filled with mock values.
    """

    return RepositorySchema(
        id="mock-repo",
        name=name,
        owner=owner,
        url=url,
        description="Mock repository summary",
        stars=0,
        forks=0,
        primary_language="Unknown",
        languages=[],
        file_count=0,
        dir_count=0,
        total_lines=0,
        last_updated="",
    )


def mock_review_result(
    task_id: str,
    repository_url: str,
    branch: str,
    owner: str,
    name: str,
) -> ReviewSchema:
    """
    Build a placeholder completed review payload.

    Args:
        task_id: Review task identifier.
        repository_url: Submitted repository URL.
        branch: Submitted Git branch.
        owner: GitHub owner name.
        name: Repository name.

    Returns:
        Review schema filled with mock values.
    """

    return ReviewSchema(
        id=task_id,
        repository_url=repository_url,
        branch=branch,
        repository=mock_repository(owner, name, repository_url),
        metrics=empty_metrics(),
        issue_severity=empty_severity(),
        files=[],
        issues_by_category=empty_categories(),
        created_at="",
        status="completed",
        progress=100,
        current_step="Report Generation",
    )
