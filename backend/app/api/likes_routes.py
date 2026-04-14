from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from ..config_data.logger_config import logger
from ..database import ManagerLikes, get_session, ManagerTweets, Likes
from ..schemas import schemas as schema
from ..utils.auth import check_auth

def register_like_routes(app):
    @app.post(
        "/api/tweets/{id}/likes",
        status_code=201,
        tags=["likes"],
        response_model=schema.ServerBoolAnswer,
        summary="Поставить лайк на твит",
    )
    async def rout_create_like_tweet(
        id: int,
        api_key: str = Header(..., description="API-ключ пользователя"),
        session: AsyncSession = Depends(get_session),
    ):
        """Создание лайка"""
        logger.debug("Создание лайка")

        user = await check_auth(session, api_key)

        object_tweet = await ManagerTweets.get_by_id(session, id)

        new_like = Likes()

        user.likes.append(new_like)
        object_tweet.likes.append(new_like)

        session.add(new_like)

        await session.flush()

        return schema.ServerBoolAnswer()

    @app.delete(
        "/api/tweets/{id}/likes",
        status_code=200,
        tags=["likes"],
        response_model=schema.ServerBoolAnswer,
        summary="Убрать отметку нравится с твита",
    )
    async def rout_delete_like_tweet(
        id: int,
        api_key: str = Header(..., description="API-ключ пользователя"),
        session: AsyncSession = Depends(get_session),
    ):
        """Удаление лайка"""
        logger.debug("Удаление лайка")

        user = await check_auth(session, api_key)

        object_tweet = await ManagerTweets.get_by_id(session, id)

        object_likes = await ManagerLikes.get_by_user_id_and_tweet_id(
            session, user.user_id, object_tweet.tweet_id
        )

        await session.delete(object_likes)

        return schema.ServerBoolAnswer()
