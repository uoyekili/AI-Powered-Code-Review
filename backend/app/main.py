"""FastAPI application entry point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import review
from app.config.settings import get_settings
from app.core.exceptions import AppError
from app.core.logging import setup_logging
from app.database.session import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Configure logging and dispose the database engine."""

    setup_logging()
    logger.info("Application started")
    yield
    await engine.dispose()
    logger.info("Application shutdown")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI instance.
    """

    settings = get_settings()
    app = FastAPI(
        title="AI GitHub Code Review API",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    app.include_router(review.router, prefix=settings.api_prefix, tags=["review"])
    return app


app = create_app()
