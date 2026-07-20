"""Health-check response schemas."""

from __future__ import annotations

from app.schemas.common import CamelModel


class HealthResponse(CamelModel):
    """Application and database health status."""

    status: str
    database: str
