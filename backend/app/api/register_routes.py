from fastapi import FastAPI
from sqlalchemy import select

from ..config_data.logger_config import logger
from ..database import (
    Base,
    User,
    async_session,
    engine,
)

from .user_routes import register_user_routes
from .tweet_routes import register_tweet_routes
from .media_routes import register_media_routes
from .likes_routes import register_like_routes

def register_routes(app: FastAPI):
    register_user_routes(app)
    register_tweet_routes(app)
    register_media_routes(app)
    register_like_routes(app)

def create_app():
    app = FastAPI()

    @app.on_event("startup")
    async def startup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.debug("База успешно создана")

        async with async_session() as session:
            db_users = await session.execute(select(User))
            object_users = db_users.scalars().all()

            if not object_users:
                users_data = [
                    User(name="Bob", api_key="test"),
                ]

                session.add_all(users_data)
                await session.flush()
                logger.debug("Добавлено {} пользователей", len(object_users))

        logger.debug("В базе уже есть пользователи")

    @app.on_event("shutdown")
    async def shutdown():
        await async_session.close()
        await engine.dispose()
        logger.debug("Сессия завершена")


    register_routes(app)

    return app