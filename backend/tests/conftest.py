import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import database.models

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
database.models.DATABASE_URL = TEST_DATABASE_URL 
database.models.engine = create_async_engine(TEST_DATABASE_URL, echo=True)
database.models.async_session = sessionmaker(
    database.models.engine, class_=AsyncSession, expire_on_commit=False
)

from app import create_app
# from database.database_models import Client, Parking
# from database.models import Base

Client = ...
Parking = ...
Base = ...

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Создает таблицы и тестовые данные для каждого теста"""
    async with database.models.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with database.models.async_session() as session:
        async with session.begin():
            from sqlalchemy import select
            
            result = await session.execute(select(Client))
            existing_clients = result.scalars().all()
            
            if not existing_clients:
                client_data = {
                    "name": "Иван",
                    "surname": "Петров",
                    "credit_card": "1234-5678-9012-3456",
                    "car_number": "А123БВ777",
                }
                db_client = Client(**client_data)
                session.add(db_client)

            result = await session.execute(select(Parking))
            existing_parkings = result.scalars().all()
            
            if not existing_parkings:
                parking_data = {
                    "address": "ул. Ленина, д. 10",
                    "opened": True,
                    "count_places": 50,
                    "count_available_places": 50,
                }
                db_parking = Parking(**parking_data)
                session.add(db_parking)

    yield

    async with database.models.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def app():
    _app = create_app()
    _app.router.on_shutdown = []
    return _app


@pytest.fixture
def client(app):
    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def db_session():
    async with database.models.async_session() as session:
        yield session
        await session.close()