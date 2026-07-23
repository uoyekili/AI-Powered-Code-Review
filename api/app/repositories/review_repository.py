"""Persistence helpers for normalized review records."""

from __future__ import annotations

import uuid

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

DEFAULT_STEPS = [
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
    """Create and read normalized review records for the API."""

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
