import logging
import uuid
from collections import Counter
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.core.exceptions import InvalidGitHubUrlError, ReviewNotFoundError
from app.models import ReviewStatus, StepStatus
from app.repositories.review_repository import ReviewRepository
from app.services.github_service import GitHubService
from app.services.langchain_service import LangChainService
from app.services.report_service import ReviewMapper, generate_markdown_report
from app.services.repo_scanner import RepoScannerService
from app.utils.file_utils import chunk_text
from app.utils.github_url import parse_github_url

logger = logging.getLogger(__name__)


class ReviewOrchestrator:
    STEP_PROGRESS = [5, 15, 30, 45, 60, 75, 90, 100]

    def __init__(self) -> None:
        self.github = GitHubService()
        self.scanner = RepoScannerService()
        self.llm = LangChainService()

    async def submit_review(self, session: AsyncSession, repository_url: str) -> str:
        repo_info = parse_github_url(repository_url)
        if not repo_info:
            raise InvalidGitHubUrlError()

        repo = ReviewRepository(session)
        task = await repo.create_task(repository_url)
        await session.commit()
        return str(task.id)

    async def get_review(self, session: AsyncSession, task_id: str):
        repo = ReviewRepository(session)
        task = await repo.get_task(uuid.UUID(task_id))
        if not task:
            raise ReviewNotFoundError(task_id)
        if not task.repository or not task.review_result:
            raise ReviewNotFoundError(task_id)
        return ReviewMapper.to_review_schema(task)

    async def get_progress(self, session: AsyncSession, task_id: str):
        repo = ReviewRepository(session)
        task = await repo.get_task(uuid.UUID(task_id))
        if not task:
            raise ReviewNotFoundError(task_id)
        return ReviewMapper.to_progress_response(task)

    async def get_report(self, session: AsyncSession, task_id: str) -> str:
        repo = ReviewRepository(session)
        task = await repo.get_task(uuid.UUID(task_id))
        if not task:
            raise ReviewNotFoundError(task_id)
        if task.report:
            return task.report.markdown_content
        if task.repository and task.review_result:
            return generate_markdown_report(task)
        raise ReviewNotFoundError(task_id)

    async def run_review(self, task_id: str) -> None:
        from app.database.session import AsyncSessionLocal

        clone_path: Path | None = None
        async with AsyncSessionLocal() as session:
            repo = ReviewRepository(session)
            task = await repo.get_task(uuid.UUID(task_id))
            if not task:
                logger.error("Task %s not found for background processing", task_id)
                return

            repo_info = parse_github_url(task.repository_url)
            if not repo_info:
                await repo.update_task_progress(
                    task,
                    status=ReviewStatus.FAILED.value,
                    error_message="Invalid GitHub URL",
                )
                await session.commit()
                return

            try:
                await self._set_step(repo, task, 0, StepStatus.IN_PROGRESS.value, "Repository Cloning")
                metadata = await self.github.fetch_metadata(repo_info)
                clone_path = self.github.clone_repository(repo_info, task_id)
                await self._complete_step(repo, task, 0, 1)

                await self._set_step(repo, task, 1, StepStatus.IN_PROGRESS.value, "Code Parsing")
                scan = self.scanner.scan(clone_path)
                await self._complete_step(repo, task, 1, 2)

                await repo.save_repository(
                    task,
                    {
                        "name": repo_info.name,
                        "owner": repo_info.owner,
                        "url": repo_info.url,
                        "description": metadata.description,
                        "stars": metadata.stars,
                        "forks": metadata.forks,
                        "primary_language": scan.primary_language or metadata.primary_language,
                        "languages": scan.languages,
                        "file_count": scan.file_count,
                        "dir_count": scan.dir_count,
                        "total_lines": scan.total_lines,
                        "last_updated": metadata.last_updated,
                    },
                )
                await session.commit()

                file_reviews: list[dict] = []
                settings = get_settings()

                await self._set_step(repo, task, 2, StepStatus.IN_PROGRESS.value, "Security Analysis")

                for scanned_file in scan.files:
                    chunks = chunk_text(scanned_file.content, settings.chunk_size_chars)
                    chunk_results = []
                    for chunk in chunks[:3]:
                        result = await self.llm.review_file(
                            owner=repo_info.owner,
                            repo=repo_info.name,
                            file_path=scanned_file.path,
                            extension=scanned_file.extension,
                            content=chunk,
                            line_count=scanned_file.lines,
                        )
                        chunk_results.append(result)

                    merged = self._merge_file_results(chunk_results)
                    file_reviews.append(
                        {
                            "path": scanned_file.path,
                            "name": scanned_file.name,
                            "extension": scanned_file.extension,
                            "lines": scanned_file.lines,
                            "summary": merged.get("summary", ""),
                            "score": int(merged.get("score", 70)),
                            "issues": merged.get("issues", []),
                        }
                    )

                analysis_steps = [
                    (2, "Security Analysis"),
                    (3, "Performance Analysis"),
                    (4, "Code Quality Check"),
                    (5, "Architecture Review"),
                ]
                for idx, name in analysis_steps:
                    await repo.update_step_status(task, idx, StepStatus.COMPLETED.value)
                await repo.update_task_progress(
                    task, progress=self.STEP_PROGRESS[6], current_step="Architecture Review"
                )
                await session.commit()

                metadata_summary = "\n".join(
                    f"--- {path} ---\n{content[:500]}" for path, content in scan.metadata_content.items()
                )
                file_summaries = "\n".join(
                    f"- {fr['path']}: score={fr['score']}, issues={len(fr['issues'])}, summary={fr['summary'][:200]}"
                    for fr in file_reviews
                )

                aggregate = await self.llm.aggregate_review(
                    owner=repo_info.owner,
                    repo=repo_info.name,
                    primary_language=scan.primary_language,
                    metadata_summary=metadata_summary or "No metadata files found.",
                    file_summaries=file_summaries or "No source files reviewed.",
                )

                severity, categories = self._compute_stats(file_reviews, aggregate)

                await self._set_step(repo, task, 6, StepStatus.IN_PROGRESS.value, "Report Generation")
                await repo.save_review_result(
                    task,
                    metrics={
                        "overall_score": int(aggregate["metrics"]["overall_score"]),
                        "security_score": int(aggregate["metrics"]["security_score"]),
                        "performance_score": int(aggregate["metrics"]["performance_score"]),
                        "maintainability_score": int(aggregate["metrics"]["maintainability_score"]),
                        "code_quality_score": int(aggregate["metrics"]["code_quality_score"]),
                        "architecture_score": int(aggregate["metrics"]["architecture_score"]),
                    },
                    severity=severity,
                    categories=categories,
                    file_reviews=file_reviews,
                )
                await session.commit()

                refreshed = await repo.get_task(uuid.UUID(task_id))
                if refreshed:
                    markdown = generate_markdown_report(refreshed)
                    await repo.save_report(refreshed, markdown)
                    await repo.update_step_status(refreshed, 6, StepStatus.COMPLETED.value)
                    await repo.update_task_progress(
                        refreshed,
                        progress=100,
                        current_step="Analysis Complete",
                        status=ReviewStatus.COMPLETED.value,
                    )
                await session.commit()
                logger.info("Review task %s completed successfully", task_id)

            except Exception as exc:
                logger.exception("Review task %s failed: %s", task_id, exc)
                await repo.update_task_progress(
                    task,
                    status=ReviewStatus.FAILED.value,
                    error_message=str(exc),
                    current_step="Analysis Failed",
                )
                for step in sorted(task.steps, key=lambda s: s.order_index):
                    if step.status == StepStatus.IN_PROGRESS.value:
                        step.status = StepStatus.FAILED.value
                await session.commit()
            finally:
                if clone_path:
                    self.github.cleanup_clone(clone_path)

    async def _set_step(
        self,
        repo: ReviewRepository,
        task,
        step_index: int,
        status: str,
        current_step: str,
    ) -> None:
        progress = self.STEP_PROGRESS[min(step_index, len(self.STEP_PROGRESS) - 1)]
        await repo.update_step_status(task, step_index, status)
        await repo.update_task_progress(
            task,
            progress=progress,
            current_step=current_step,
            status=ReviewStatus.IN_PROGRESS.value,
        )

    async def _complete_step(self, repo: ReviewRepository, task, step_index: int, next_progress_index: int) -> None:
        await repo.update_step_status(task, step_index, StepStatus.COMPLETED.value)
        await repo.update_task_progress(task, progress=self.STEP_PROGRESS[next_progress_index])

    @staticmethod
    def _merge_file_results(results: list[dict]) -> dict:
        if not results:
            return {"summary": "", "score": 70, "issues": []}
        if len(results) == 1:
            return results[0]

        all_issues = []
        scores = []
        summaries = []
        for result in results:
            scores.append(int(result.get("score", 70)))
            summaries.append(result.get("summary", ""))
            all_issues.extend(result.get("issues", []))

        seen_titles = set()
        unique_issues = []
        for issue in all_issues:
            key = (issue.get("title"), issue.get("line"))
            if key not in seen_titles:
                seen_titles.add(key)
                unique_issues.append(issue)

        return {
            "summary": " ".join(summaries)[:500],
            "score": sum(scores) // len(scores),
            "issues": unique_issues[:10],
        }

    @staticmethod
    def _compute_stats(file_reviews: list[dict], aggregate: dict) -> tuple[dict, dict]:
        severity_counter: Counter[str] = Counter()
        category_counter: Counter[str] = Counter()

        for file_review in file_reviews:
            for issue in file_review.get("issues", []):
                severity_counter[issue.get("severity", "info")] += 1
                issue_type = issue.get("type", "code-quality")
                if issue_type == "code-quality":
                    category_counter["code_quality"] += 1
                else:
                    category_counter[issue_type.replace("-", "_")] += 1

        severity = {
            "critical": severity_counter.get("critical", 0),
            "high": severity_counter.get("high", 0),
            "medium": severity_counter.get("medium", 0),
            "low": severity_counter.get("low", 0),
            "info": severity_counter.get("info", 0),
        }
        categories = {
            "security": category_counter.get("security", 0),
            "performance": category_counter.get("performance", 0),
            "maintainability": category_counter.get("maintainability", 0),
            "code_quality": category_counter.get("code_quality", 0),
            "architecture": category_counter.get("architecture", 0),
        }

        agg_severity = aggregate.get("issue_severity", {})
        agg_categories = aggregate.get("issues_by_category", {})

        for key in severity:
            severity[key] = max(severity[key], int(agg_severity.get(key, 0)))
        for key in categories:
            categories[key] = max(categories[key], int(agg_categories.get(key, 0)))

        return severity, categories
