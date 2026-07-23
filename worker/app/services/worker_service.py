"""Background worker orchestration for review pipeline tasks."""

from __future__ import annotations

import logging
import uuid

from app.database.session import AsyncSessionLocal
from database.models import ReviewStatus, StepStatus
from app.repositories.review_repository import ReviewRepository
from app.review.pipeline import PipelineContext, ReviewPipeline
from app.schemas.review_fixtures import mock_review_result
from app.services.report_service import ReportService
from app.utils.github_url import parse_github_url

logger = logging.getLogger(__name__)


class WorkerService:
    """Run the review pipeline for a single claimed task."""

    def __init__(self) -> None:
        self.pipeline = ReviewPipeline()
        self.report_service = ReportService()

    async def process_task(self, task_id: str) -> None:
        """
        Process one review task using the mock pipeline.

        Args:
            task_id: Review task identifier.
        """

        try:
            task_uuid = uuid.UUID(task_id)
        except ValueError:
            logger.error("Invalid task id: %s", task_id)
            return

        async with AsyncSessionLocal() as session:
            repository = ReviewRepository(session)
            task = await repository.get_task(task_uuid)
            if task is None:
                logger.error("Task not found: %s", task_id)
                return

            try:
                await repository.update_progress(
                    task,
                    status=ReviewStatus.IN_PROGRESS.value,
                    progress=5,
                    current_step="Clone Repository",
                )
                await session.commit()

                context = PipelineContext(task.repository_url, task.branch)
                try:
                    total = len(task.steps)
                    for index, step in enumerate(task.steps):
                        await repository.update_step(step, StepStatus.IN_PROGRESS)
                        await repository.update_progress(
                            task,
                            progress=int(((index + 0.5) / total) * 100),
                            current_step=step.name,
                        )
                        await session.commit()

                        await self.pipeline.run_step(step.step_key, context)

                        await repository.update_step(step, StepStatus.COMPLETED)
                        await repository.update_progress(
                            task,
                            progress=int(((index + 1) / total) * 100),
                            current_step=step.name,
                        )
                        await session.commit()

                    repo_info = parse_github_url(task.repository_url)
                    owner = repo_info.owner if repo_info else "unknown"
                    name = repo_info.name if repo_info else "unknown"
                    review = mock_review_result(
                        str(task.id),
                        task.repository_url,
                        task.branch,
                        owner,
                        name,
                    )
                    review.created_at = task.created_at.isoformat().replace("+00:00", "Z")
                    report = self.report_service.generate_markdown(review)

                    await repository.save_result(
                        task,
                        review.model_dump(by_alias=False, mode="json"),
                        report,
                    )
                    await session.commit()
                    logger.info("Mock review completed for task %s", task_id)
                finally:
                    context.cleanup()
            except Exception as exc:
                logger.exception("Review failed for task %s", task_id)
                await repository.update_progress(
                    task,
                    status=ReviewStatus.FAILED.value,
                    error_message=str(exc),
                    current_step="Failed",
                )
                await session.commit()
