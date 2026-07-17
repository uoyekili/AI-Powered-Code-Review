from app.models import FileReview, Report, Repository, ReviewResult, ReviewTask
from app.repositories.review_repository import ReviewRepository
from app.schemas.review_schema import (
    AnalysisStepSchema,
    CodeReviewMetricsSchema,
    FileReviewSchema,
    IssueSchema,
    IssueSeveritySchema,
    IssuesByCategorySchema,
    ProgressResponse,
    RepositorySchema,
    ReviewSchema,
)


class ReviewMapper:
    @staticmethod
    def to_review_schema(task: ReviewTask) -> ReviewSchema:
        if not task.repository or not task.review_result:
            raise ValueError("Review task is missing repository or result data")

        repo = task.repository
        result = task.review_result

        files = []
        for file_review in result.file_reviews:
            files.append(ReviewMapper._to_file_schema(file_review))

        return ReviewSchema(
            id=str(task.id),
            repository_url=task.repository_url,
            repository=ReviewMapper._to_repository_schema(repo),
            metrics=CodeReviewMetricsSchema(
                overall_score=result.overall_score,
                security_score=result.security_score,
                performance_score=result.performance_score,
                maintainability_score=result.maintainability_score,
                code_quality_score=result.code_quality_score,
                architecture_score=result.architecture_score,
            ),
            issue_severity=IssueSeveritySchema(
                critical=result.severity_critical,
                high=result.severity_high,
                medium=result.severity_medium,
                low=result.severity_low,
                info=result.severity_info,
            ),
            files=files,
            issues_by_category=IssuesByCategorySchema(
                security=result.category_security,
                performance=result.category_performance,
                maintainability=result.category_maintainability,
                code_quality=result.category_code_quality,
                architecture=result.category_architecture,
            ),
            created_at=ReviewRepository.format_datetime(task.created_at),
            status=task.status,
            progress=task.progress,
            current_step=task.current_step,
        )

    @staticmethod
    def to_progress_response(task: ReviewTask) -> ProgressResponse:
        steps = [
            AnalysisStepSchema(
                id=str(step.id),
                name=step.name,
                description=step.description,
                status=step.status,
                estimated_time=step.estimated_time,
            )
            for step in sorted(task.steps, key=lambda s: s.order_index)
        ]
        return ProgressResponse(
            progress=task.progress,
            current_step=task.current_step or "Initializing analysis...",
            steps=steps,
            status=task.status,
        )

    @staticmethod
    def _to_repository_schema(repo: Repository) -> RepositorySchema:
        return RepositorySchema(
            id=str(repo.id),
            name=repo.name,
            owner=repo.owner,
            url=repo.url,
            description=repo.description,
            stars=repo.stars,
            forks=repo.forks,
            primary_language=repo.primary_language,
            languages=repo.languages or [],
            file_count=repo.file_count,
            dir_count=repo.dir_count,
            total_lines=repo.total_lines,
            last_updated=ReviewRepository.format_datetime(repo.last_updated),
        )

    @staticmethod
    def _to_file_schema(file_review: FileReview) -> FileReviewSchema:
        return FileReviewSchema(
            path=file_review.path,
            name=file_review.name,
            extension=file_review.extension,
            lines=file_review.lines,
            summary=file_review.summary,
            score=file_review.score,
            issues=[
                IssueSchema(
                    id=str(issue.id),
                    file=issue.file_path,
                    line=issue.line,
                    type=issue.type,
                    severity=issue.severity,
                    title=issue.title,
                    description=issue.description,
                    suggestion=issue.suggestion,
                    code=issue.code,
                )
                for issue in file_review.issues
            ],
        )


def generate_markdown_report(task: ReviewTask) -> str:
    review = ReviewMapper.to_review_schema(task)
    lines: list[str] = []

    lines.append("# AI Code Review Report")
    lines.append(f"Generated: {review.created_at}")
    lines.append("")

    lines.append("## Repository Information")
    lines.append(
        f"- **Repository**: [{review.repository.owner}/{review.repository.name}]({review.repository.url})"
    )
    lines.append(f"- **Description**: {review.repository.description}")
    lines.append(f"- **Language**: {review.repository.primary_language}")
    lines.append(f"- **Stars**: {review.repository.stars:,}")
    lines.append(f"- **Forks**: {review.repository.forks:,}")
    lines.append("")

    lines.append("## Review Scores")
    lines.append("| Category | Score |")
    lines.append("|----------|-------|")
    lines.append(f"| Overall | {review.metrics.overall_score}/100 |")
    lines.append(f"| Security | {review.metrics.security_score}/100 |")
    lines.append(f"| Performance | {review.metrics.performance_score}/100 |")
    lines.append(f"| Maintainability | {review.metrics.maintainability_score}/100 |")
    lines.append(f"| Code Quality | {review.metrics.code_quality_score}/100 |")
    lines.append(f"| Architecture | {review.metrics.architecture_score}/100 |")
    lines.append("")

    lines.append("## Issues Summary")
    lines.append("| Severity | Count |")
    lines.append("|----------|-------|")
    lines.append(f"| Critical | {review.issue_severity.critical} |")
    lines.append(f"| High | {review.issue_severity.high} |")
    lines.append(f"| Medium | {review.issue_severity.medium} |")
    lines.append(f"| Low | {review.issue_severity.low} |")
    lines.append(f"| Info | {review.issue_severity.info} |")
    lines.append("")

    lines.append("## Issues by Category")
    lines.append(f"- Security: {review.issues_by_category.security}")
    lines.append(f"- Performance: {review.issues_by_category.performance}")
    lines.append(f"- Maintainability: {review.issues_by_category.maintainability}")
    lines.append(f"- Code Quality: {review.issues_by_category.code_quality}")
    lines.append(f"- Architecture: {review.issues_by_category.architecture}")
    lines.append("")

    lines.append("## Files Reviewed")
    for file in review.files:
        lines.append(f"### {file.path}")
        lines.append(f"- **Lines**: {file.lines}")
        lines.append(f"- **Score**: {file.score}/100")
        lines.append(f"- **Issues**: {len(file.issues)}")
        lines.append(f"\n{file.summary}")
        lines.append("")

        if file.issues:
            lines.append("#### Issues:")
            for issue in file.issues:
                lines.append(f"- **[{issue.severity.upper()}]** {issue.title} (Line {issue.line})")
                lines.append(f"  - {issue.description}")
                lines.append(f"  - **Suggestion**: {issue.suggestion}")
            lines.append("")

    lines.append("---")
    lines.append(
        "_This report was generated by AI GitHub Code Review Assistant. "
        "Recommendations are suggestions and should be reviewed by developers._"
    )

    return "\n".join(lines)
