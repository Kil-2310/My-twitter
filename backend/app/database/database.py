from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from ..config_data.config import DB_NAME, DB_PASSWORD, DB_USER

# Для продакшена
engine = create_async_engine(
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@postgres:5432/{DB_NAME}"
)

# Для локальной разработки
# engine = create_async_engine("sqlite+aiosqlite:///./app.db", echo=True)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()
