# app/db/database.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


# Resolve database URL from environment (via Pydantic Settings) with a safe fallback
def get_database_url() -> str:
    if settings.DATABASE_URL:
        return settings.DATABASE_URL
    # Fallback to local SQLite database file using async driver
    return "sqlite+aiosqlite:///./resume_jobs.db"

DATABASE_URL = get_database_url()

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    future=True,
)

# Async session maker
async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Base for models
class Base(DeclarativeBase):
    pass

# Dependency for FastAPI (async)
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
