"""HTTP routes for health checks and review operations."""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from sqlalchemy import text

from app.api.dependencies import DatabaseSession, ReviewServiceDependency
from app.schemas.review_schema import (
    HealthResponse,
    ProgressResponse,
    ReviewSchema,
    SubmitReviewRequest,
    SubmitReviewResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(session: DatabaseSession) -> HealthResponse:
    """Return API and database health status."""

    db_status = "ok"
    try:
        await session.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error("Database health check failed: %s", exc)
        db_status = "error"

    return HealthResponse(
        status="ok" if db_status == "ok" else "degraded",
        database=db_status,
    )


@router.post("/review", response_model=SubmitReviewResponse)
async def submit_review(
    payload: SubmitReviewRequest,
    service: ReviewServiceDependency,
) -> SubmitReviewResponse:
    """
    Accept a repository URL and start a review task.

    Args:
        payload: Submit review request.
        service: Review application service.

    Returns:
        Created review identifier.
    """

    review_id = await service.submit_review(payload.repository_url, payload.branch)
    return SubmitReviewResponse(review_id=review_id)


@router.get("/review/{task_id}", response_model=ReviewSchema)
async def get_review(
    task_id: uuid.UUID,
    service: ReviewServiceDependency,
) -> ReviewSchema:
    """
    Return the review result for a task.

    Args:
        task_id: Review task UUID.
        service: Review application service.

    Returns:
        Review response payload.
    """

    return await service.get_review(str(task_id))


@router.get("/review/{task_id}/progress", response_model=ProgressResponse)
async def get_progress(
    task_id: uuid.UUID,
    service: ReviewServiceDependency,
) -> ProgressResponse:
    """
    Return progress for a review task.

    Args:
        task_id: Review task UUID.
        service: Review application service.

    Returns:
        Progress response payload.
    """

    return await service.get_progress(str(task_id))


@router.get("/report/{task_id}", response_class=PlainTextResponse)
async def get_report(
    task_id: uuid.UUID,
    service: ReviewServiceDependency,
) -> PlainTextResponse:
    """
    Download the Markdown report for a review task.

    Args:
        task_id: Review task UUID.
        service: Review application service.

    Returns:
        Markdown report as plain text.
    """

    content = await service.get_report(str(task_id))
    return PlainTextResponse(content, media_type="text/markdown; charset=utf-8")
