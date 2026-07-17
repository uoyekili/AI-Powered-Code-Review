from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class SubmitReviewRequest(CamelModel):
    repository_url: str = Field(..., min_length=1, alias="repositoryUrl")


class SubmitReviewResponse(CamelModel):
    review_id: str


class RepositorySchema(CamelModel):
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
    overall_score: int
    security_score: int
    performance_score: int
    maintainability_score: int
    code_quality_score: int
    architecture_score: int


class IssueSeveritySchema(CamelModel):
    critical: int
    high: int
    medium: int
    low: int
    info: int


class IssueSchema(CamelModel):
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
    path: str
    name: str
    extension: str
    lines: int
    issues: list[IssueSchema]
    summary: str
    score: int


class IssuesByCategorySchema(CamelModel):
    security: int
    performance: int
    maintainability: int
    code_quality: int
    architecture: int


class ReviewSchema(CamelModel):
    id: str
    repository_url: str
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
    id: str
    name: str
    description: str
    status: str
    estimated_time: int


class ProgressResponse(CamelModel):
    progress: int
    current_step: str
    steps: list[AnalysisStepSchema]
    status: str = "pending"


class HealthResponse(CamelModel):
    status: str
    database: str
