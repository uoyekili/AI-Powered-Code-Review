"""Persistence helpers for normalized review records."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import (
    CodeRepository,
        Review,
    ReviewFile,
    ReviewStatus,
    ReviewStep,
    StepStatus,
)
from api.app.schemas.review_response import ReviewSchema
from api.app.schemas.review_response import RepositorySchema, CodeReviewMetricsSchema, IssueSeveritySchema, IssueSchema, FileReviewSchema, IssuesByCategorySchema
from database.models import RepositoryLanguage, ReviewIssue, IssueType, IssueSeverity


class ReviewRepository:
    """Claim, update, and persist review work for the worker."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_task(self, task_id: uuid.UUID) -> Review | None:
        """
        Load a review task by identifier.

        Args:
            task_id: Review task UUID.

        Returns:
            Review task when found, otherwise None.
        """

        result = await self.session.execute(
            select(Review)
            .where(Review.id == task_id)
            .options(
                selectinload(Review.repository).selectinload(CodeRepository.languages),
                selectinload(Review.steps),
                selectinload(Review.files).selectinload(ReviewFile.issues),
                selectinload(Review.issues),
            )
        )
        return result.scalar_one_or_none()

    async def claim_pending_task(self) -> Review | None:
        """
        Claim the oldest PENDING review for processing.

        Uses SKIP LOCKED so multiple worker replicas can poll safely.
        """

        result = await self.session.execute(
            select(Review)
            .where(Review.status == ReviewStatus.PENDING)
            .order_by(Review.created_at.asc())
            .limit(1)
            .with_for_update(skip_locked=True)
            .options(selectinload(Review.steps))
        )
        task = result.scalar_one_or_none()
        if task is None:
            return None

        await self.update_progress(
            task,
            status=ReviewStatus.IN_PROGRESS.value,
            progress=0,
            current_step="Queued",
        )
        return task

    async def update_progress(
        self,
        task: Review,
        *,
        progress: int | None = None,
        current_step: str | None = None,
        status: str | None = None,
        error_message: str | None = None,
    ) -> None:
        """
        Update task progress fields.

        Args:
            task: Task to update.
            progress: Optional progress percentage.
            current_step: Optional current step label.
            status: Optional lifecycle status.
            error_message: Optional failure message.
        """

        if progress is not None:
            task.progress = progress
        if current_step is not None:
            task.current_step = current_step
        if status is not None:
            task.status = ReviewStatus(status)
            now = datetime.now(timezone.utc)
            if task.status is ReviewStatus.IN_PROGRESS and task.started_at is None:
                task.started_at = now
            if task.status in {ReviewStatus.COMPLETED, ReviewStatus.FAILED}:
                task.completed_at = now
        if error_message is not None:
            task.error_message = error_message
        await self.session.flush()

    async def update_step(
        self,
        step: ReviewStep,
        status: StepStatus,
    ) -> None:
        """Update one pipeline step and its lifecycle timestamps."""

        step.status = status
        now = datetime.now(timezone.utc)
        if status is StepStatus.IN_PROGRESS and step.started_at is None:
            step.started_at = now
        if status in {StepStatus.COMPLETED, StepStatus.FAILED}:
            step.completed_at = now
        await self.session.flush()

    async def save_result(
        self,
        task: Review,
        result: ReviewSchema,
        report_markdown: str,
    ) -> None:
        """
        Persist the completed review payload and report.

        Args:
            task: Task to update.
            result: Serialized review result.
            report_markdown: Final Markdown report body.
        """

        repository_data = result.repository
        task.repository.description = repository_data.description
        task.repository.stars = repository_data.stars
        task.repository.forks = repository_data.forks
        task.repository.primary_language = repository_data.primary_language
        task.repository.file_count = repository_data.file_count
        task.repository.dir_count = repository_data.dir_count
        task.repository.total_lines = repository_data.total_lines
        task.repository.languages = [RepositoryLanguage(name=language) for language in repository_data.languages]

        metrics = result.metrics
        task.overall_score = metrics.overall_score
        task.security_score = metrics.security_score
        task.performance_score = metrics.performance_score
        task.maintainability_score = metrics.maintainability_score
        task.code_quality_score = metrics.code_quality_score
        task.architecture_score = metrics.architecture_score

        task.issues.clear()
        task.files.clear()
        for file_data in result.files:
            review_file = ReviewFile(
                path=file_data.path,
                name=file_data.name,
                extension=file_data.extension,
                line_count=file_data.lines,
                summary=file_data.summary,
                score=file_data.score,
            )
            task.files.append(review_file)
            for issue_data in file_data.issues:
                task.issues.append(
                    ReviewIssue(
                        file=review_file,
                        external_id=issue_data.id,
                        file_path=issue_data.file,
                        line_number=issue_data.line,
                        type=IssueType(issue_data.type),
                        severity=IssueSeverity(issue_data.severity),
                        title=issue_data.title,
                        description=issue_data.description,
                        suggestion=issue_data.suggestion,
                        code_snippet=issue_data.code,
                    )
                )

        task.report_markdown = report_markdown
        task.status = ReviewStatus.COMPLETED
        task.progress = 100
        task.completed_at = datetime.now(timezone.utc)
        await self.session.flush()
