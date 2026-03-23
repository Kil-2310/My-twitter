from fastapi import FastAPI

from ..database.database import engine, Base, async_session


def create_app():

    app = FastAPI()

    @app.on_event("startup")
    async def startup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @app.on_event("shutdown")
    async def shutdown():
        await async_session.close()
        await engine.dispose()

    return app
