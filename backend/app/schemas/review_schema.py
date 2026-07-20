"""Pydantic request and response schemas for the review API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Base model that serializes fields as camelCase."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class SubmitReviewRequest(CamelModel):
    """Payload for creating a new review task."""

    repository_url: str = Field(..., min_length=1)
    branch: str = Field(..., min_length=1, max_length=255)

    @field_validator("branch")
    @classmethod
    def validate_branch(cls, value: str) -> str:
        """Validate a conservative Git branch/ref name accepted by the MVP."""

        branch = value.strip()
        forbidden_characters = set("~^:?*[\\")
        if (
            not branch
            or branch.startswith(("-", ".", "/"))
            or branch.endswith((".", "/"))
            or ".." in branch
            or "//" in branch
            or "@{" in branch
            or any(
                character.isspace() or character in forbidden_characters
                for character in branch
            )
        ):
            raise ValueError("must be a valid Git branch name")
        return branch


class SubmitReviewResponse(CamelModel):
    """Response returned after a review task is accepted."""

    review_id: str


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


class AnalysisStepSchema(CamelModel):
    """One step in the analysis pipeline progress UI."""

    id: str
    name: str
    description: str
    status: str
    estimated_time: int


class ProgressResponse(CamelModel):
    """Progress payload used while a review is running."""

    progress: int
    current_step: str
    steps: list[AnalysisStepSchema]
    status: str = "pending"


class HealthResponse(CamelModel):
    """Application and database health status."""

    status: str
    database: str


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
