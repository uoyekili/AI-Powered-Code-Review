"""Persistence helpers for normalized review records."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    CodeRepository,
    IssueSeverity,
    IssueType,
    RepositoryLanguage,
    Review,
    ReviewFile,
    ReviewIssue,
    ReviewStatus,
    ReviewStep,
    StepStatus,
)

DEFAULT_STEPS: list[dict[str, Any]] = [
    {
        "id": "clone",
        "name": "Clone Repository",
        "description": "Clone the GitHub repository",
        "status": StepStatus.PENDING.value,
        "estimated_time": 20,
    },
    {
        "id": "scan",
        "name": "Repository Scanner",
        "description": "Detect language, framework, and project structure",
        "status": StepStatus.PENDING.value,
        "estimated_time": 30,
    },
    {
        "id": "static",
        "name": "Static Analysis",
        "description": "Run lint, security, and complexity checks",
        "status": StepStatus.PENDING.value,
        "estimated_time": 40,
    },
    {
        "id": "chunk",
        "name": "Repository Chunking",
        "description": "Split the project into logical code chunks",
        "status": StepStatus.PENDING.value,
        "estimated_time": 20,
    },
    {
        "id": "llm",
        "name": "Parallel LLM Review",
        "description": "Review code chunks with LLM workers",
        "status": StepStatus.PENDING.value,
        "estimated_time": 60,
    },
    {
        "id": "merge",
        "name": "Merge Review Results",
        "description": "Merge issues, rank severity, and calculate scores",
        "status": StepStatus.PENDING.value,
        "estimated_time": 20,
    },
    {
        "id": "report",
        "name": "Generate Final Report",
        "description": "Build the final review report",
        "status": StepStatus.PENDING.value,
        "estimated_time": 15,
    },
]


class ReviewRepository:
    """CRUD and state updates for normalized review records."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_task(
        self,
        repository_url: str,
        owner: str,
        name: str,
        branch: str,
    ) -> Review:
        """
        Create a pending review task.

        Args:
            repository_url: Validated GitHub repository URL.
            owner: GitHub repository owner.
            name: GitHub repository name.
            branch: Git branch to review.

        Returns:
            Persisted review task.
        """

        code_repository = await self._get_or_create_repository(
            repository_url,
            owner,
            name,
        )
        task = Review(
            repository=code_repository,
            branch=branch,
            status=ReviewStatus.PENDING,
            progress=0,
            current_step="",
            steps=[
                ReviewStep(
                    step_key=step["id"],
                    position=position,
                    name=step["name"],
                    description=step["description"],
                    status=StepStatus.PENDING,
                    estimated_time=step["estimated_time"],
                )
                for position, step in enumerate(DEFAULT_STEPS)
            ],
        )
        self.session.add(task)
        await self.session.flush()
        return task

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
        result: dict[str, Any],
        report_markdown: str,
    ) -> None:
        """
        Persist the completed review payload and report.

        Args:
            task: Task to update.
            result: Serialized review result.
            report_markdown: Final Markdown report body.
        """

        repository_data = result.get("repository", {})
        task.repository.description = repository_data.get("description", "")
        task.repository.stars = repository_data.get("stars", 0)
        task.repository.forks = repository_data.get("forks", 0)
        task.repository.primary_language = repository_data.get(
            "primary_language", "Unknown"
        )
        task.repository.file_count = repository_data.get("file_count", 0)
        task.repository.dir_count = repository_data.get("dir_count", 0)
        task.repository.total_lines = repository_data.get("total_lines", 0)
        task.repository.languages = [
            RepositoryLanguage(name=language)
            for language in repository_data.get("languages", [])
        ]

        metrics = result.get("metrics", {})
        task.overall_score = metrics.get("overall_score", 0)
        task.security_score = metrics.get("security_score", 0)
        task.performance_score = metrics.get("performance_score", 0)
        task.maintainability_score = metrics.get("maintainability_score", 0)
        task.code_quality_score = metrics.get("code_quality_score", 0)
        task.architecture_score = metrics.get("architecture_score", 0)

        task.issues.clear()
        task.files.clear()
        for file_data in result.get("files", []):
            review_file = ReviewFile(
                path=file_data["path"],
                name=file_data["name"],
                extension=file_data.get("extension", ""),
                line_count=file_data.get("lines", 0),
                summary=file_data.get("summary", ""),
                score=file_data.get("score", 0),
            )
            task.files.append(review_file)
            for issue_data in file_data.get("issues", []):
                task.issues.append(
                    ReviewIssue(
                        file=review_file,
                        external_id=issue_data.get("id"),
                        file_path=issue_data.get("file", review_file.path),
                        line_number=issue_data.get("line", 0),
                        type=IssueType(issue_data["type"]),
                        severity=IssueSeverity(issue_data["severity"]),
                        title=issue_data["title"],
                        description=issue_data.get("description", ""),
                        suggestion=issue_data.get("suggestion", ""),
                        code_snippet=issue_data.get("code"),
                    )
                )

        task.report_markdown = report_markdown
        task.status = ReviewStatus.COMPLETED
        task.progress = 100
        task.completed_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def _get_or_create_repository(
        self,
        repository_url: str,
        owner: str,
        name: str,
    ) -> CodeRepository:
        result = await self.session.execute(
            select(CodeRepository).where(CodeRepository.url == repository_url)
        )
        code_repository = result.scalar_one_or_none()
        if code_repository is None:
            code_repository = CodeRepository(
                url=repository_url,
                owner=owner,
                name=name,
            )
            self.session.add(code_repository)
            await self.session.flush()
        return code_repository
