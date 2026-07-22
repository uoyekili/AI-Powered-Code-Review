"""Response schemas for a completed review payload."""

from __future__ import annotations

from app.schemas.common import CamelModel


class RepositorySchema(CamelModel):
    """Repository metadata shown in the review dashboard."""

    id: str
    name: str
    owner: str
    url: str
    description: str
    stars: int
    forks: int
    primary_language: str
    languages: list[str]
    file_count: int
    dir_count: int
    total_lines: int
    last_updated: str


class CodeReviewMetricsSchema(CamelModel):
    """Aggregate quality scores for a reviewed repository."""

    overall_score: int
    security_score: int
    performance_score: int
    maintainability_score: int
    code_quality_score: int
    architecture_score: int


class IssueSeveritySchema(CamelModel):
    """Issue counts grouped by severity."""

    critical: int
    high: int
    medium: int
    low: int
    info: int


class IssueSchema(CamelModel):
    """A single review finding."""

    id: str
    file: str
    line: int
    type: str
    severity: str
    title: str
    description: str
    suggestion: str
    code: str | None = None


class FileReviewSchema(CamelModel):
    """Per-file review summary."""

    path: str
    name: str
    extension: str
    lines: int
    issues: list[IssueSchema]
    summary: str
    score: int


class IssuesByCategorySchema(CamelModel):
    """Issue counts grouped by category."""

    security: int
    performance: int
    maintainability: int
    code_quality: int
    architecture: int


class ReviewSchema(CamelModel):
    """Full review result returned to the frontend."""

    id: str
    repository_url: str
    branch: str
    repository: RepositorySchema
    metrics: CodeReviewMetricsSchema
    issue_severity: IssueSeveritySchema
    files: list[FileReviewSchema]
    issues_by_category: IssuesByCategorySchema
    created_at: str
    status: str
    progress: int
    current_step: str
