from fastapi import FastAPI

from ..database import engine, Base, async_session
from ..config_data.logger_config import logger


def create_app():

    app = FastAPI()

    @app.on_event("startup")
    async def startup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.debug("База успешно создана")

    @app.on_event("shutdown")
    async def shutdown():
        await async_session.close()
        await engine.dispose()
        logger.debug("Сессия завершена")

    return app
