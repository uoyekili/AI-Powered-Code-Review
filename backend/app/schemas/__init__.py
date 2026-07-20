"""Pydantic schema package."""

from app.schemas.common import CamelModel
from app.schemas.health import HealthResponse
from app.schemas.progress import AnalysisStepSchema, ProgressResponse
from app.schemas.review_fixtures import (
    empty_categories,
    empty_metrics,
    empty_severity,
    mock_repository,
    mock_review_result,
)
from app.schemas.review_request import SubmitReviewRequest, SubmitReviewResponse
from app.schemas.review_response import (
    CodeReviewMetricsSchema,
    FileReviewSchema,
    IssueSchema,
    IssueSeveritySchema,
    IssuesByCategorySchema,
    RepositorySchema,
    ReviewSchema,
)

__all__ = [
    "AnalysisStepSchema",
    "CamelModel",
    "CodeReviewMetricsSchema",
    "FileReviewSchema",
    "HealthResponse",
    "IssueSchema",
    "IssueSeveritySchema",
    "IssuesByCategorySchema",
    "ProgressResponse",
    "RepositorySchema",
    "ReviewSchema",
    "SubmitReviewRequest",
    "SubmitReviewResponse",
    "empty_categories",
    "empty_metrics",
    "empty_severity",
    "mock_repository",
    "mock_review_result",
]
