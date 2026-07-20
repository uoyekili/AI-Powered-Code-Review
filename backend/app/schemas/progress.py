"""Progress schemas for an in-flight review."""

from __future__ import annotations

from app.schemas.common import CamelModel


class AnalysisStepSchema(CamelModel):
    """One step in the analysis pipeline progress UI."""

    id: str
    name: str
    description: str
    status: str
    estimated_time: int


class ProgressResponse(CamelModel):
    """Progress payload used while a review is running."""

    progress: int
    current_step: str
    steps: list[AnalysisStepSchema]
    status: str = "pending"
