"""
Test configuration and fixtures for the Band Manager API.

This module provides:
- Test database setup and teardown
- Common fixtures for test data
- Test client configuration
- Authentication testing utilities
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
import uuid
from typing import AsyncGenerator, Dict, Any
from unittest.mock import patch
import jwt

# Import your application modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import get_db
from models import Base
from repository import BandRepository
from auth import get_current_user, get_current_user_optional

# Test database configuration
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create a test database engine that uses in-memory SQLite"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False  # Set to True for SQL debugging
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    await engine.dispose()

@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session with proper cleanup"""
    TestSessionLocal = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # Create a connection and transaction for this test
    connection = await test_engine.connect()
    transaction = await connection.begin()
    
    # Create a session bound to this connection
    session = AsyncSession(bind=connection, expire_on_commit=False)
    
    try:
        yield session
    finally:
        # Close the session
        await session.close()
        # Rollback the transaction to clean up all changes
        await transaction.rollback()
        # Close the connection
        await connection.close()

@pytest.fixture
async def test_repo(test_session) -> BandRepository:
    """Create a test repository instance"""
    return BandRepository(test_session)

@pytest.fixture
def test_client(test_session):
    """Create a test client with dependency override"""
    
    async def override_get_db():
        yield test_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    # Clean up dependency override
    app.dependency_overrides.clear()

@pytest.fixture
async def async_client(test_session) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client"""
    
    async def override_get_db():
        yield test_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Clean up dependency override
    app.dependency_overrides.clear()

# Test data fixtures
@pytest.fixture
def sample_user_id():
    """Generate a consistent user ID for tests"""
    return uuid.UUID("12345678-1234-5678-1234-567812345678")

@pytest.fixture
def sample_user_id_2():
    """Generate a second consistent user ID for tests"""
    return uuid.UUID("87654321-4321-8765-4321-876543218765")

@pytest.fixture
def mock_user_1():
    """Mock authenticated user data for testing"""
    return {
        "user_id": "12345678-1234-5678-1234-567812345678",
        "email": "test@example.com",
        "role": "authenticated",
        "aud": "authenticated",
        "exp": 9999999999,  # Far future
        "iat": 1000000000
    }

@pytest.fixture
def mock_user_2():
    """Mock second authenticated user data for testing"""
    return {
        "user_id": "87654321-4321-8765-4321-876543218765",
        "email": "test2@example.com",
        "role": "authenticated",
        "aud": "authenticated",
        "exp": 9999999999,  # Far future
        "iat": 1000000000
    }

@pytest.fixture
def auth_headers_user_1():
    """Generate valid auth headers for mock user 1"""
    return {"Authorization": "Bearer valid-jwt-token-user-1"}

@pytest.fixture
def auth_headers_user_2():
    """Generate valid auth headers for mock user 2"""
    return {"Authorization": "Bearer valid-jwt-token-user-2"}

@pytest.fixture
def mock_auth_user_1(mock_user_1):
    """Mock authentication dependency to return user 1"""
    async def mock_get_current_user():
        return mock_user_1
    return mock_get_current_user

@pytest.fixture
def mock_auth_user_2(mock_user_2):
    """Mock authentication dependency to return user 2"""
    async def mock_get_current_user():
        return mock_user_2
    return mock_get_current_user

@pytest.fixture
def authenticated_client_user_1(test_session, mock_auth_user_1):
    """Test client authenticated as user 1"""
    async def override_get_db():
        yield test_session
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = mock_auth_user_1
    app.dependency_overrides[get_current_user_optional] = mock_auth_user_1
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()

@pytest.fixture
def authenticated_client_user_2(test_session, mock_auth_user_2):
    """Test client authenticated as user 2"""
    async def override_get_db():
        yield test_session
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = mock_auth_user_2
    app.dependency_overrides[get_current_user_optional] = mock_auth_user_2
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()

@pytest.fixture
def unauthenticated_client(test_session):
    """Test client without authentication"""
    async def override_get_db():
        yield test_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()

@pytest.fixture
def sample_profile_data():
    """Sample profile creation data"""
    return {
        "display_name": "Test User",
        "email": "test@example.com"
    }

@pytest.fixture
def sample_band_data():
    """Sample band creation data"""
    return {
        "name": "Test Band",
        "timezone": "America/New_York"
    }

@pytest.fixture
def sample_venue_data():
    """Sample venue creation data"""
    return {
        "name": "Test Venue",
        "address": "123 Test Street, Test City",
        "notes": "This is a test venue"
    }

@pytest.fixture
def sample_event_data():
    """Sample event creation data"""
    from datetime import datetime, timezone
    
    return {
        "title": "Test Rehearsal",
        "starts_at_utc": datetime(2025, 10, 15, 19, 0, 0, tzinfo=timezone.utc),
        "ends_at_utc": datetime(2025, 10, 15, 21, 0, 0, tzinfo=timezone.utc),
        "type": "rehearsal",
        "notes": "This is a test rehearsal"
    }

# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    import asyncio
    
    # Set asyncio event loop policy for consistent behavior
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())