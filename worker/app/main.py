"""Worker entry point: health endpoint and pending-task poller."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.config.settings import get_settings
from app.core.logging import setup_logging
from app.database.session import AsyncSessionLocal, engine
from app.repositories.review_repository import ReviewRepository
from app.services.worker_service import WorkerService

logger = logging.getLogger(__name__)


async def poll_pending_tasks(stop_event: asyncio.Event) -> None:
    """Claim and process PENDING review tasks until stopped."""

    settings = get_settings()
    worker = WorkerService()

    while not stop_event.is_set():
        task_id: str | None = None
        try:
            async with AsyncSessionLocal() as session:
                repository = ReviewRepository(session)
                task = await repository.claim_pending_task()
                if task is not None:
                    task_id = str(task.id)
                await session.commit()

            if task_id is not None:
                logger.info("Claimed review task %s", task_id)
                await worker.process_task(task_id)
            else:
                try:
                    await asyncio.wait_for(
                        stop_event.wait(),
                        timeout=settings.poll_interval_seconds,
                    )
                except TimeoutError:
                    pass
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Poll loop error")
            await asyncio.sleep(settings.poll_interval_seconds)


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    stop_event = asyncio.Event()
    poller = asyncio.create_task(poll_pending_tasks(stop_event), name="review-poller")
    logger.info("Worker started")
    try:
        yield
    finally:
        stop_event.set()
        poller.cancel()
        try:
            await poller
        except asyncio.CancelledError:
            pass
        await engine.dispose()
        logger.info("Worker shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI GitHub Code Review Worker",
        version="0.1.0",
        lifespan=lifespan,
        description="Background worker that processes pending review tasks.",
    )

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        db_status = "ok"
        try:
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
        except Exception as exc:
            logger.error("Database health check failed: %s", exc)
            db_status = "error"

        return {
            "status": "ok" if db_status == "ok" else "degraded",
            "database": db_status,
            "role": "worker",
        }

    return app


app = create_app()
