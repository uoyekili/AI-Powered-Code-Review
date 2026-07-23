"""ORM models for file-level review findings."""

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
from database.models.enums import IssueSeverity, IssueType, enum_values

if TYPE_CHECKING:
    from database.models.review import Review


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
    __table_args__ = (CheckConstraint("line_number >= 0", name="ck_review_issues_line_number"),)

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
