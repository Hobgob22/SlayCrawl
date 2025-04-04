from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, DateTime, Text, Integer
from datetime import datetime
import os
from typing import AsyncGenerator

Base = declarative_base()

class APIKeyModel(Base):
    """SQLAlchemy model for API keys."""
    __tablename__ = "api_keys"
    
    key = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_used = Column(DateTime)

class ScrapedDataModel(Base):
    """SQLAlchemy model for scraped data."""
    __tablename__ = "scraped_data"
    
    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False, index=True)
    title = Column(String)
    content = Column(Text)
    page_metadata = Column(Text)  # store metadata as JSON text
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    cached = Column(String, index=True)  # Cache key in Redis

# Database URL from environment variable with fallback
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///scraper.db")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True if os.getenv("LOG_LEVEL") == "DEBUG" else False
)

# Create async session factory
async_session_factory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Initialize the database with required tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
