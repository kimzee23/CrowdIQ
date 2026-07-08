import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from main import app
from src.infrastructure.persistence.repository.database import get_db
from src.infrastructure.persistence.models import Base

# We use an in-memory SQLite database for testing to avoid needing a live Postgres instance.
# Note: SQLite has some differences from Postgres, but for MVP testing it's sufficient.
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)

test_async_session_factory = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with test_async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_test_db():
    async with test_engine.begin() as conn:
        # Create all tables in the in-memory SQLite database
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def mock_redis_store():
    return {}


@pytest.fixture(autouse=True)
def mock_redis_and_celery(monkeypatch, mock_redis_store):
    async def fake_set(key, value, ttl=300):
        mock_redis_store[key] = value

    async def fake_get(key):
        return mock_redis_store.get(key)

    async def fake_delete(key):
        mock_redis_store.pop(key, None)

    monkeypatch.setattr("src.domain.service.user.cache_set", fake_set)
    monkeypatch.setattr("src.domain.service.user.cache_get", fake_get)
    monkeypatch.setattr("src.domain.service.user.cache_delete", fake_delete)

    monkeypatch.setattr("src.domain.service.user.send_email_notification.delay", lambda *a, **kw: None)
