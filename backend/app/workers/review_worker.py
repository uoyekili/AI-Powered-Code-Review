import asyncio
import logging

from app.services.review_service import ReviewOrchestrator

logger = logging.getLogger(__name__)
_orchestrator = ReviewOrchestrator()


def enqueue_review_task(task_id: str) -> None:
    asyncio.create_task(_run_with_logging(task_id))


async def _run_with_logging(task_id: str) -> None:
    logger.info("Starting background review for task %s", task_id)
    await _orchestrator.run_review(task_id)
