"""In-process background task adapter for review jobs."""

from __future__ import annotations

import asyncio
import logging

logger = logging.getLogger(__name__)


def enqueue_review_task(task_id: str) -> None:
    """
    Enqueue a review task for background processing.

    Args:
        task_id: Review task identifier.

    TODO:
        Replace asyncio.create_task with a durable queue and parallel workers.
    """

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        logger.error("No running event loop; cannot enqueue task %s", task_id)
        return

    loop.create_task(_run_task(task_id))


async def _run_task(task_id: str) -> None:
    """Run the worker service for one task."""

    from app.services.worker_service import WorkerService

    worker = WorkerService()
    await worker.process_task(task_id)
