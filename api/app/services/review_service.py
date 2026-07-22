"""Application service for review task orchestration."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidGitHubUrlError, ReviewNotFoundError
from app.models import IssueSeverity, IssueType, Review, ReviewStatus
from app.repositories.review_repository import ReviewRepository
from app.schemas.progress import AnalysisStepSchema, ProgressResponse
from app.schemas.review_response import (
    CodeReviewMetricsSchema,
    FileReviewSchema,
    IssuesByCategorySchema,
    IssueSchema,
    IssueSeveritySchema,
    RepositorySchema,
    ReviewSchema,
)
from app.utils.github_url import parse_github_url


class ReviewService:
    """Validate requests, persist tasks, and expose review reads."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ReviewRepository(session)

    async def submit_review(self, repository_url: str, branch: str) -> str:
        """
        Accept a repository URL and create a pending review task.

        The worker polls for PENDING tasks and processes them asynchronously.

        Args:
            repository_url: GitHub repository URL.
            branch: Git branch to review.

        Returns:
            Created review task identifier.

        Raises:
            InvalidGitHubUrlError: If the URL is not a valid GitHub repository.
        """

        repo_info = parse_github_url(repository_url)
        if repo_info is None:
            raise InvalidGitHubUrlError()

        task = await self.repository.create_task(
            repo_info.url,
            repo_info.owner,
            repo_info.name,
            branch,
        )
        await self.session.commit()
        return str(task.id)

    async def get_review(self, task_id: str) -> ReviewSchema:
        task = await self._get_task_or_raise(task_id)
        return self._to_review_schema(task)

    async def get_progress(self, task_id: str) -> ProgressResponse:
        task = await self._get_task_or_raise(task_id)
        steps = [
            AnalysisStepSchema(
                id=step.step_key,
                name=step.name,
                description=step.description,
                status=step.status.value,
                estimated_time=step.estimated_time,
            )
            for step in task.steps
        ]
        return ProgressResponse(
            progress=task.progress,
            current_step=task.current_step,
            steps=steps,
            status=task.status.value,
        )

    async def get_report(self, task_id: str) -> str:
        task = await self._get_task_or_raise(task_id)
        if not task.report_markdown:
            if task.status is not ReviewStatus.COMPLETED:
                raise ReviewNotFoundError(task_id)
            return (
                f"# Code Review Report\n\n"
                f"Repository: {task.repository_url}\n\n"
                f"Branch: {task.branch}\n"
            )
        return task.report_markdown

    async def _get_task_or_raise(self, task_id: str):
        try:
            task_uuid = uuid.UUID(task_id)
        except ValueError as exc:
            raise ReviewNotFoundError(task_id) from exc

        task = await self.repository.get_task(task_uuid)
        if task is None:
            raise ReviewNotFoundError(task_id)
        return task

    @staticmethod
    def _format_datetime(value: datetime | None) -> str:
        if value is None:
            return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        return value.isoformat().replace("+00:00", "Z")

    def _to_review_schema(self, task: Review) -> ReviewSchema:
        repository = task.repository
        severity_counts = {severity.value: 0 for severity in IssueSeverity}
        category_counts = {issue_type.value: 0 for issue_type in IssueType}
        for issue in task.issues:
            severity_counts[issue.severity.value] += 1
            category_counts[issue.type.value] += 1

        files = [
            FileReviewSchema(
                path=review_file.path,
                name=review_file.name,
                extension=review_file.extension,
                lines=review_file.line_count,
                issues=[
                    IssueSchema(
                        id=issue.external_id or str(issue.id),
                        file=issue.file_path,
                        line=issue.line_number,
                        type=issue.type.value,
                        severity=issue.severity.value,
                        title=issue.title,
                        description=issue.description,
                        suggestion=issue.suggestion,
                        code=issue.code_snippet,
                    )
                    for issue in review_file.issues
                ],
                summary=review_file.summary,
                score=review_file.score,
            )
            for review_file in task.files
        ]

        return ReviewSchema(
            id=str(task.id),
            repository_url=repository.url,
            branch=task.branch,
            repository=RepositorySchema(
                id=str(repository.id),
                name=repository.name,
                owner=repository.owner,
                url=repository.url,
                description=repository.description,
                stars=repository.stars,
                forks=repository.forks,
                primary_language=repository.primary_language,
                languages=[language.name for language in repository.languages],
                file_count=repository.file_count,
                dir_count=repository.dir_count,
                total_lines=repository.total_lines,
                last_updated=self._format_datetime(repository.last_updated_at),
            ),
            metrics=CodeReviewMetricsSchema(
                overall_score=task.overall_score,
                security_score=task.security_score,
                performance_score=task.performance_score,
                maintainability_score=task.maintainability_score,
                code_quality_score=task.code_quality_score,
                architecture_score=task.architecture_score,
            ),
            issue_severity=IssueSeveritySchema(**severity_counts),
            files=files,
            issues_by_category=IssuesByCategorySchema(
                security=category_counts["security"],
                performance=category_counts["performance"],
                maintainability=category_counts["maintainability"],
                code_quality=category_counts["code-quality"],
                architecture=category_counts["architecture"],
            ),
            created_at=self._format_datetime(task.created_at),
            status=task.status.value,
            progress=task.progress,
            current_step=task.current_step,
        )
