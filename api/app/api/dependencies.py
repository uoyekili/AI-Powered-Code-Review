"""Reusable FastAPI dependency aliases."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.services.review_service import ReviewService

DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


def get_review_service(session: DatabaseSession) -> ReviewService:
    """Build a review service for the request session."""

    return ReviewService(session)


ReviewServiceDependency = Annotated[
    ReviewService,
    Depends(get_review_service),
]
