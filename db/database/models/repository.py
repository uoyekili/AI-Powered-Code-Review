"""ORM models for Git repositories."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from database.models.review import Review


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
    primary_language: Mapped[str] = mapped_column(String(100), default="Unknown", nullable=False)
    file_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    dir_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_lines: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
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
