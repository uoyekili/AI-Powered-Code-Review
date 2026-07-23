"""Shared enum types persisted on review-related tables."""

from __future__ import annotations

import enum


class ReviewStatus(str, enum.Enum):
    """Lifecycle status of a review task."""

    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    FAILED = "failed"


class StepStatus(str, enum.Enum):
    """Lifecycle status of a single analysis step."""

    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    FAILED = "failed"


class IssueType(str, enum.Enum):
    """Issue category labels used by the API contract."""

    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    CODE_QUALITY = "code-quality"
    ARCHITECTURE = "architecture"


class IssueSeverity(str, enum.Enum):
    """Issue severity labels used by the API contract."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


def enum_values(enum_class: type[enum.Enum]) -> list[str]:
    """Persist string enum values instead of Python member names."""

    return [str(member.value) for member in enum_class]
