"""ORM models for review runs and pipeline steps."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

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

from database.base import Base
from database.models.enums import ReviewStatus, StepStatus, enum_values

if TYPE_CHECKING:
    from database.models.finding import ReviewFile, ReviewIssue
    from database.models.repository import CodeRepository


class Review(Base):
    """One review run and its aggregate progress and quality scores."""

    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("progress BETWEEN 0 AND 100", name="ck_reviews_progress"),
        CheckConstraint("overall_score BETWEEN 0 AND 100", name="ck_reviews_overall_score"),
        CheckConstraint("security_score BETWEEN 0 AND 100", name="ck_reviews_security_score"),
        CheckConstraint("performance_score BETWEEN 0 AND 100", name="ck_reviews_performance_score"),
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
    maintainability_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    code_quality_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    architecture_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
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
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    review: Mapped[Review] = relationship(back_populates="steps")
