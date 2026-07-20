"""Normalized ORM models for repository review data."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


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


class CodeRepository(Base):
    """Git repository that can have multiple review runs."""

    __tablename__ = "repositories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    url: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    stars: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    forks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    primary_language: Mapped[str] = mapped_column(
        String(100), default="Unknown", nullable=False
    )
    file_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    dir_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_lines: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    reviews: Mapped[list[Review]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
    )
    languages: Mapped[list[RepositoryLanguage]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        order_by="RepositoryLanguage.name",
    )


class RepositoryLanguage(Base):
    """Language detected in a repository."""

    __tablename__ = "repository_languages"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(String(100), primary_key=True)

    repository: Mapped[CodeRepository] = relationship(back_populates="languages")


class Review(Base):
    """One review run and its aggregate progress and quality scores."""

    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("progress BETWEEN 0 AND 100", name="ck_reviews_progress"),
        CheckConstraint(
            "overall_score BETWEEN 0 AND 100", name="ck_reviews_overall_score"
        ),
        CheckConstraint(
            "security_score BETWEEN 0 AND 100", name="ck_reviews_security_score"
        ),
        CheckConstraint(
            "performance_score BETWEEN 0 AND 100", name="ck_reviews_performance_score"
        ),
        CheckConstraint(
            "maintainability_score BETWEEN 0 AND 100",
            name="ck_reviews_maintainability_score",
        ),
        CheckConstraint(
            "code_quality_score BETWEEN 0 AND 100",
            name="ck_reviews_code_quality_score",
        ),
        CheckConstraint(
            "architecture_score BETWEEN 0 AND 100",
            name="ck_reviews_architecture_score",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    branch: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[ReviewStatus] = mapped_column(
        Enum(
            ReviewStatus,
            values_callable=enum_values,
            native_enum=False,
            create_constraint=True,
            name="review_status",
            length=32,
        ),
        default=ReviewStatus.PENDING.value,
        nullable=False,
        index=True,
    )
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_step: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    report_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    overall_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    security_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    performance_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    maintainability_score: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    code_quality_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    architecture_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    repository: Mapped[CodeRepository] = relationship(back_populates="reviews")
    steps: Mapped[list[ReviewStep]] = relationship(
        back_populates="review",
        cascade="all, delete-orphan",
        order_by="ReviewStep.position",
    )
    files: Mapped[list[ReviewFile]] = relationship(
        back_populates="review",
        cascade="all, delete-orphan",
        order_by="ReviewFile.path",
    )
    issues: Mapped[list[ReviewIssue]] = relationship(
        back_populates="review",
        cascade="all, delete-orphan",
    )

    @property
    def repository_url(self) -> str:
        """Keep the service-facing URL accessor concise."""

        return self.repository.url


class ReviewStep(Base):
    """Persisted progress state for one review pipeline stage."""

    __tablename__ = "review_steps"
    __table_args__ = (
        UniqueConstraint("review_id", "step_key", name="uq_review_steps_review_key"),
        CheckConstraint("position >= 0", name="ck_review_steps_position"),
        CheckConstraint("estimated_time >= 0", name="ck_review_steps_estimated_time"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    review_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_key: Mapped[str] = mapped_column(String(64), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[StepStatus] = mapped_column(
        Enum(
            StepStatus,
            values_callable=enum_values,
            native_enum=False,
            create_constraint=True,
            name="step_status",
            length=32,
        ),
        default=StepStatus.PENDING.value,
        nullable=False,
    )
    estimated_time: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    review: Mapped[Review] = relationship(back_populates="steps")


class ReviewFile(Base):
    """File-level summary produced by a review run."""

    __tablename__ = "review_files"
    __table_args__ = (
        UniqueConstraint("review_id", "path", name="uq_review_files_review_path"),
        CheckConstraint("line_count >= 0", name="ck_review_files_line_count"),
        CheckConstraint("score BETWEEN 0 AND 100", name="ck_review_files_score"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    review_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    path: Mapped[str] = mapped_column(String(1024), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    extension: Mapped[str] = mapped_column(String(50), default="", nullable=False)
    line_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    review: Mapped[Review] = relationship(back_populates="files")
    issues: Mapped[list[ReviewIssue]] = relationship(
        back_populates="file",
        cascade="all, delete-orphan",
    )


class ReviewIssue(Base):
    """One normalized finding attached to a review and optionally a file."""

    __tablename__ = "review_issues"
    __table_args__ = (
        CheckConstraint("line_number >= 0", name="ck_review_issues_line_number"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    review_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("review_files.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_path: Mapped[str] = mapped_column(String(1024), default="", nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    type: Mapped[IssueType] = mapped_column(
        Enum(
            IssueType,
            values_callable=enum_values,
            native_enum=False,
            create_constraint=True,
            name="issue_type",
            length=32,
        ),
        nullable=False,
        index=True,
    )
    severity: Mapped[IssueSeverity] = mapped_column(
        Enum(
            IssueSeverity,
            values_callable=enum_values,
            native_enum=False,
            create_constraint=True,
            name="issue_severity",
            length=32,
        ),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    suggestion: Mapped[str] = mapped_column(Text, default="", nullable=False)
    code_snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    review: Mapped[Review] = relationship(back_populates="issues")
    file: Mapped[ReviewFile | None] = relationship(back_populates="issues")
