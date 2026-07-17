import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.database.session import get_db
from app.schemas.review_schema import (
    HealthResponse,
    ProgressResponse,
    ReviewSchema,
    SubmitReviewRequest,
    SubmitReviewResponse,
)
from app.services.review_service import ReviewOrchestrator
from app.workers.review_worker import enqueue_review_task

logger = logging.getLogger(__name__)
router = APIRouter()
orchestrator = ReviewOrchestrator()


def _handle_app_error(exc: AppError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=exc.message)


@router.get("/health", response_model=HealthResponse)
async def health_check(session: AsyncSession = Depends(get_db)) -> HealthResponse:
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
    session: AsyncSession = Depends(get_db),
) -> SubmitReviewResponse:
    try:
        review_id = await orchestrator.submit_review(session, payload.repository_url)
        enqueue_review_task(review_id)
        return SubmitReviewResponse(review_id=review_id)
    except AppError as exc:
        raise _handle_app_error(exc) from exc


@router.get("/review/{task_id}", response_model=ReviewSchema)
async def get_review(
    task_id: str,
    session: AsyncSession = Depends(get_db),
) -> ReviewSchema:
    try:
        return await orchestrator.get_review(session, task_id)
    except AppError as exc:
        raise _handle_app_error(exc) from exc


@router.get("/review/{task_id}/progress", response_model=ProgressResponse)
async def get_progress(
    task_id: str,
    session: AsyncSession = Depends(get_db),
) -> ProgressResponse:
    try:
        return await orchestrator.get_progress(session, task_id)
    except AppError as exc:
        raise _handle_app_error(exc) from exc


@router.get("/report/{task_id}", response_class=PlainTextResponse)
async def get_report(
    task_id: str,
    session: AsyncSession = Depends(get_db),
) -> PlainTextResponse:
    try:
        content = await orchestrator.get_report(session, task_id)
        return PlainTextResponse(content, media_type="text/markdown; charset=utf-8")
    except AppError as exc:
        raise _handle_app_error(exc) from exc
