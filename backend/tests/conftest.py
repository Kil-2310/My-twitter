import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from backend.app.database.database import Base
from backend.app.api.register_routes import create_app

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(autouse=True, scope="function")
async def setup_database():
    """Создаёт таблицы перед каждым тестом и удаляет после"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture(scope="function")
def app():
    """Возвращает экземпляр приложения FastAPI"""
    return create_app()


@pytest.fixture(scope="function")
def client(app):
    """Тестовый клиент FastAPI"""
    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Асинхронная сессия для прямого доступа к БД"""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()
        await session.close()
