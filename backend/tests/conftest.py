# /tests/conftest.py
# This file is the "setup" for all your tests.

import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi.testclient import TestClient

from backend.src.config.main import app  # Import your main FastAPI app
from backend.src.config.database import Base, get_session # Import your real get_session

# --- 1. Create a Test Database ---
# We use an in-memory SQLite database
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL)
test_session_factory = async_sessionmaker(test_engine, expire_on_commit=False)

# --- 2. Create the Test Database Tables ---
@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_tables():
    """
    This fixture runs once per session. It creates all database tables.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # (No teardown needed for in-memory DB)

# --- 3. Override the 'get_session' Dependency ---
# This is the most important part.
# We replace the real 'get_session' with this function.
async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    A dependency override that provides a test database session.
    """
    async with test_session_factory() as session:
        yield session

# Tell the FastAPI app to use our new function
app.dependency_overrides[get_session] = override_get_session

# --- 4. Create the 'TestClient' Fixture ---
# This 'client' is what your tests will use to make API calls.
@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """
    A fixture that provides a TestClient for making API requests.
    """
    with TestClient(app) as c:
        yield c