"""Report generation interfaces."""

from __future__ import annotations

from app.schemas.review_response import ReviewSchema


class ReportService:
    """Build the final Markdown review report."""

    def generate_markdown(self, review: ReviewSchema) -> str:
        """
        Generate a Markdown report from a review result.

        Args:
            review: Completed review payload.

        Returns:
            Markdown report body.

        TODO:
            Implement full report generation with issue details and recommendations.
        """

        return (
            f"# Code Review Report\n\n"
            f"Repository: {review.repository_url}\n\n"
            f"Branch: {review.branch}\n\n"
            f"Overall score: {review.metrics.overall_score}\n\n"
            f"_Mock report. Replace with real generation._\n"
        )

    def merge_results(
        self,
        chunk_results: list[dict],
        static_issues: list[dict],
    ) -> dict:
        """
        Merge chunk reviews and static findings into one result.

        Args:
            chunk_results: Findings from LLM chunk reviews.
            static_issues: Findings from static analysis.

        Returns:
            Merged result dictionary.

        TODO:
            Implement issue merge, deduplication, severity ranking, and scoring.
        """

        return {
            "chunk_results": chunk_results,
            "static_issues": static_issues,
            "files": [],
            "metrics": {
                "overall_score": 0,
                "security_score": 0,
                "performance_score": 0,
                "maintainability_score": 0,
                "code_quality_score": 0,
                "architecture_score": 0,
            },
        }
