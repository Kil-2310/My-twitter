from fastapi import FastAPI

from ..database import engine, Base, async_session, User
from ..config_data.logger_config import logger


def create_app():

    app = FastAPI()

    @app.on_event("startup")
    async def startup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.debug("База успешно создана")

        async with async_session() as session:
            users = [
                User(name="Bob", api_key="123"),
                User(name="Tom", api_key="456"),
                User(name="Alice", api_key="789"),
            ]

            session.add_all(users)
            await session.commit()
            logger.debug("Добавлено {} пользователей", len(users))

    @app.on_event("shutdown")
    async def shutdown():
        await async_session.close()
        await engine.dispose()
        logger.debug("Сессия завершена")

    return app
