import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    AnalysisStep,
    FileReview,
    Issue,
    Report,
    Repository,
    ReviewResult,
    ReviewStatus,
    ReviewTask,
    StepStatus,
)

DEFAULT_STEPS = [
    ("Repository Cloning", "Cloning repository and preparing for analysis", 30),
    ("Code Parsing", "Parsing and analyzing code structure", 45),
    ("Security Analysis", "Scanning for security vulnerabilities", 60),
    ("Performance Analysis", "Analyzing performance patterns and bottlenecks", 50),
    ("Code Quality Check", "Evaluating code quality and best practices", 55),
    ("Architecture Review", "Assessing overall architecture and design patterns", 40),
    ("Report Generation", "Generating comprehensive review report", 20),
]


class ReviewRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_task(self, repository_url: str) -> ReviewTask:
        task = ReviewTask(repository_url=repository_url, status=ReviewStatus.PENDING.value)
        self.session.add(task)
        await self.session.flush()

        for index, (name, description, estimated_time) in enumerate(DEFAULT_STEPS):
            self.session.add(
                AnalysisStep(
                    task_id=task.id,
                    name=name,
                    description=description,
                    estimated_time=estimated_time,
                    order_index=index,
                    status=StepStatus.PENDING.value,
                )
            )

        await self.session.flush()
        return task

    async def get_task(self, task_id: uuid.UUID) -> ReviewTask | None:
        result = await self.session.execute(
            select(ReviewTask)
            .where(ReviewTask.id == task_id)
            .options(
                selectinload(ReviewTask.repository),
                selectinload(ReviewTask.steps),
                selectinload(ReviewTask.review_result)
                .selectinload(ReviewResult.file_reviews)
                .selectinload(FileReview.issues),
                selectinload(ReviewTask.report),
            )
        )
        return result.scalar_one_or_none()

    async def update_task_progress(
        self,
        task: ReviewTask,
        *,
        progress: int | None = None,
        current_step: str | None = None,
        status: str | None = None,
        error_message: str | None = None,
    ) -> None:
        if progress is not None:
            task.progress = progress
        if current_step is not None:
            task.current_step = current_step
        if status is not None:
            task.status = status
        if error_message is not None:
            task.error_message = error_message
        await self.session.flush()

    async def update_step_status(
        self,
        task: ReviewTask,
        step_index: int,
        status: str,
    ) -> None:
        steps = sorted(task.steps, key=lambda s: s.order_index)
        if 0 <= step_index < len(steps):
            steps[step_index].status = status
            await self.session.flush()

    async def save_repository(self, task: ReviewTask, data: dict) -> Repository:
        repo = Repository(task_id=task.id, **data)
        self.session.add(repo)
        await self.session.flush()
        return repo

    async def save_review_result(
        self,
        task: ReviewTask,
        metrics: dict,
        severity: dict,
        categories: dict,
        file_reviews: list[dict],
    ) -> ReviewResult:
        result = ReviewResult(
            task_id=task.id,
            overall_score=metrics["overall_score"],
            security_score=metrics["security_score"],
            performance_score=metrics["performance_score"],
            maintainability_score=metrics["maintainability_score"],
            code_quality_score=metrics["code_quality_score"],
            architecture_score=metrics["architecture_score"],
            severity_critical=severity["critical"],
            severity_high=severity["high"],
            severity_medium=severity["medium"],
            severity_low=severity["low"],
            severity_info=severity["info"],
            category_security=categories["security"],
            category_performance=categories["performance"],
            category_maintainability=categories["maintainability"],
            category_code_quality=categories["code_quality"],
            category_architecture=categories["architecture"],
        )
        self.session.add(result)
        await self.session.flush()

        for file_data in file_reviews:
            file_review = FileReview(
                review_result_id=result.id,
                path=file_data["path"],
                name=file_data["name"],
                extension=file_data["extension"],
                lines=file_data["lines"],
                summary=file_data["summary"],
                score=file_data["score"],
            )
            self.session.add(file_review)
            await self.session.flush()

            for issue_data in file_data.get("issues", []):
                self.session.add(
                    Issue(
                        file_review_id=file_review.id,
                        file_path=file_data["path"],
                        line=issue_data.get("line", 1),
                        type=issue_data["type"],
                        severity=issue_data["severity"],
                        title=issue_data["title"],
                        description=issue_data["description"],
                        suggestion=issue_data["suggestion"],
                        code=issue_data.get("code"),
                    )
                )

        await self.session.flush()
        return result

    async def save_report(self, task: ReviewTask, markdown_content: str) -> Report:
        report = Report(task_id=task.id, markdown_content=markdown_content)
        self.session.add(report)
        await self.session.flush()
        return report

    @staticmethod
    def format_datetime(value: datetime | None) -> str:
        if value is None:
            return datetime.utcnow().isoformat() + "Z"
        return value.isoformat().replace("+00:00", "Z")
