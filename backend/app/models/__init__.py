import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ReviewStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    FAILED = "failed"


class StepStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    FAILED = "failed"


class IssueType(str, enum.Enum):
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    CODE_QUALITY = "code-quality"
    ARCHITECTURE = "architecture"


class IssueSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ReviewTask(Base):
    __tablename__ = "review_tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repository_url: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default=ReviewStatus.PENDING.value, nullable=False)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_step: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    repository: Mapped["Repository | None"] = relationship(back_populates="task", uselist=False, cascade="all, delete-orphan")
    steps: Mapped[list["AnalysisStep"]] = relationship(
        back_populates="task", cascade="all, delete-orphan", order_by="AnalysisStep.order_index"
    )
    review_result: Mapped["ReviewResult | None"] = relationship(
        back_populates="task", uselist=False, cascade="all, delete-orphan"
    )
    report: Mapped["Report | None"] = relationship(back_populates="task", uselist=False, cascade="all, delete-orphan")


class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("review_tasks.id", ondelete="CASCADE"), unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    stars: Mapped[int] = mapped_column(Integer, default=0)
    forks: Mapped[int] = mapped_column(Integer, default=0)
    primary_language: Mapped[str] = mapped_column(String(64), default="Unknown")
    languages: Mapped[list] = mapped_column(JSONB, default=list)
    file_count: Mapped[int] = mapped_column(Integer, default=0)
    dir_count: Mapped[int] = mapped_column(Integer, default=0)
    total_lines: Mapped[int] = mapped_column(Integer, default=0)
    last_updated: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    task: Mapped["ReviewTask"] = relationship(back_populates="repository")


class AnalysisStep(Base):
    __tablename__ = "analysis_steps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("review_tasks.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default=StepStatus.PENDING.value)
    estimated_time: Mapped[int] = mapped_column(Integer, default=30)
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    task: Mapped["ReviewTask"] = relationship(back_populates="steps")


class ReviewResult(Base):
    __tablename__ = "review_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("review_tasks.id", ondelete="CASCADE"), unique=True)
    overall_score: Mapped[int] = mapped_column(Integer, default=0)
    security_score: Mapped[int] = mapped_column(Integer, default=0)
    performance_score: Mapped[int] = mapped_column(Integer, default=0)
    maintainability_score: Mapped[int] = mapped_column(Integer, default=0)
    code_quality_score: Mapped[int] = mapped_column(Integer, default=0)
    architecture_score: Mapped[int] = mapped_column(Integer, default=0)
    severity_critical: Mapped[int] = mapped_column(Integer, default=0)
    severity_high: Mapped[int] = mapped_column(Integer, default=0)
    severity_medium: Mapped[int] = mapped_column(Integer, default=0)
    severity_low: Mapped[int] = mapped_column(Integer, default=0)
    severity_info: Mapped[int] = mapped_column(Integer, default=0)
    category_security: Mapped[int] = mapped_column(Integer, default=0)
    category_performance: Mapped[int] = mapped_column(Integer, default=0)
    category_maintainability: Mapped[int] = mapped_column(Integer, default=0)
    category_code_quality: Mapped[int] = mapped_column(Integer, default=0)
    category_architecture: Mapped[int] = mapped_column(Integer, default=0)

    task: Mapped["ReviewTask"] = relationship(back_populates="review_result")
    file_reviews: Mapped[list["FileReview"]] = relationship(
        back_populates="review_result", cascade="all, delete-orphan"
    )


class FileReview(Base):
    __tablename__ = "file_reviews"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_result_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("review_results.id", ondelete="CASCADE")
    )
    path: Mapped[str] = mapped_column(String(1024), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    extension: Mapped[str] = mapped_column(String(32), default="")
    lines: Mapped[int] = mapped_column(Integer, default=0)
    summary: Mapped[str] = mapped_column(Text, default="")
    score: Mapped[int] = mapped_column(Integer, default=0)

    review_result: Mapped["ReviewResult"] = relationship(back_populates="file_reviews")
    issues: Mapped[list["Issue"]] = relationship(back_populates="file_review", cascade="all, delete-orphan")


class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_review_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("file_reviews.id", ondelete="CASCADE")
    )
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    line: Mapped[int] = mapped_column(Integer, default=1)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    suggestion: Mapped[str] = mapped_column(Text, nullable=False)
    code: Mapped[str | None] = mapped_column(Text, nullable=True)

    file_review: Mapped["FileReview"] = relationship(back_populates="issues")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("review_tasks.id", ondelete="CASCADE"), unique=True)
    markdown_content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    task: Mapped["ReviewTask"] = relationship(back_populates="report")
