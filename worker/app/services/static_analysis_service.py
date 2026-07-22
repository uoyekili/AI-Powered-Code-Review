"""Static analysis interfaces."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class StaticAnalysisResult:
    """Placeholder result from static analysis tools."""

    issues: list[dict] = field(default_factory=list)
    complexity: dict = field(default_factory=dict)
    duplicates: list[str] = field(default_factory=list)


class StaticAnalysisService:
    """Run lint, security, and complexity checks."""

    def analyze(self, path: Path) -> StaticAnalysisResult:
        """
        Run static analysis on a repository.

        Args:
            path: Local repository path.

        Returns:
            Static analysis result.

        TODO:
            Implement parsing, linting, security scan, complexity, and duplicate detection.
        """

        return StaticAnalysisResult()
