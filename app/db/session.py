from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


_engine: Optional[AsyncEngine] = None
async_session_maker: Optional[async_sessionmaker[AsyncSession]] = None


def get_database_url() -> Optional[str]:
    """Return the database URL or a sensible default SQLite URL.

    If settings.DATABASE_URL is not provided, fall back to a local SQLite database
    so the application can operate without external DB configuration.
    """
    if settings.DATABASE_URL:
        return settings.DATABASE_URL
    # Fallback to local SQLite database file
    return "sqlite+aiosqlite:///./resume_jobs.db"


def setup_engine(echo: bool = False) -> AsyncEngine:
    """Create and cache the async SQLAlchemy engine and sessionmaker."""
    global _engine, async_session_maker

    if _engine is not None and async_session_maker is not None:
        return _engine

    database_url = get_database_url()
    _engine = create_async_engine(database_url, echo=echo or settings.DEBUG, future=True)
    async_session_maker = async_sessionmaker(
        bind=_engine,
        expire_on_commit=False,
        autoflush=False,
        class_=AsyncSession,
    )
    return _engine


async def init_db() -> None:
    """Initialize the database by creating all tables."""
    engine = setup_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


