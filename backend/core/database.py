from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base  # noqa: F401
from .config import settings

# Database URLs
ASYNC_URL = settings.DATABASE_URL
SYNC_URL = settings.DATABASE_URL.replace("sqlite+aiosqlite", "sqlite")

# Async Engine
engine = create_async_engine(
    ASYNC_URL,
    echo=True,
    pool_pre_ping=True,
)

AsyncSessionLocal = sessionmaker(
    engine,   # noqa: W291
    class_=AsyncSession,   # noqa: W291
    expire_on_commit=False
)

# Sync Engine (for legacy/merged code)
sync_engine = create_engine(
    SYNC_URL,
    echo=True,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in SYNC_URL else {}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)

from ..models.orm import Base  # noqa: E402,F401

async def get_db():  # noqa: E302
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

def get_db_sync():  # noqa: E302
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
