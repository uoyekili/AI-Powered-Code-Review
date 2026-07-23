"""Async SQLAlchemy engine and session helpers."""

from __future__ import annotations

from database.session import create_engine, create_get_db, create_session_factory

from app.config.settings import get_settings

settings = get_settings()

engine = create_engine(settings.database_url)
AsyncSessionLocal = create_session_factory(engine)
get_db = create_get_db(AsyncSessionLocal)
