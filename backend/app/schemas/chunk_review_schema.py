"""Pydantic schemas for LLM chunk-review inputs and outputs."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.review import IssueSeverity, IssueType


class LLMIssueDraft(BaseModel):
    """Raw finding returned by the LLM before id and file are attached."""

    type: IssueType
    severity: IssueSeverity
    title: str = Field(min_length=1, max_length=200)
    description: str
    suggestion: str
    line: int = Field(default=0, ge=0)
    code: str


class LLMChunkReviewResponse(BaseModel):
    """Structured LLM response for a single chunk review call."""

    summary: str
    score: int = Field(default=0, ge=0, le=100)
    issues: list[LLMIssueDraft] = Field(default_factory=list)


class ChunkIssue(BaseModel):
    """Normalized finding ready for merge, persistence, and API mapping."""

    id: str
    file: str
    line: int = Field(ge=0)
    type: IssueType
    severity: IssueSeverity
    title: str
    description: str
    suggestion: str
    code: str | None = None


class ChunkReviewResult(BaseModel):
    """Aggregated review outcome for one code chunk."""

    file_path: str
    summary: str = ""
    score: int = Field(default=0, ge=0, le=100)
    issues: list[ChunkIssue] = Field(default_factory=list)
