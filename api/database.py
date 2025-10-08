"""
Database configuration and connection management using SQLAlchemy.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database settings
    database_url: str = os.getenv("DATABASE_URL", "")
    
    # Supabase settings
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY", "")
    supabase_service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    supabase_jwt_secret: str = os.getenv("SUPABASE_JWT_SECRET", "")
    
    # Database pool settings
    pool_size: int = 20
    max_overflow: int = 0
    echo: bool = False  # Set to True for SQL logging in development
    
    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings()

# Convert postgres:// to postgresql+asyncpg:// for SQLAlchemy async
def get_async_database_url(url: str) -> str:
    """Convert database URL to async format"""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url

# Create async engine
engine = create_async_engine(
    get_async_database_url(settings.database_url),
    pool_size=settings.pool_size,
    max_overflow=settings.max_overflow,
    echo=settings.echo,
    future=True
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    """
    Dependency that provides a database session.
    Use this in FastAPI route dependencies.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """
    Initialize database connection.
    Call this during application startup.
    """
    from models import Base
    
    # Create all tables (in production, use Alembic migrations instead)
    async with engine.begin() as conn:
        # Uncomment the next line if you want to recreate tables on startup
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    print("Database initialization completed")

async def close_db():
    """
    Close database connections.
    Call this during application shutdown.
    """
    await engine.dispose()
    print("Database connections closed")
