from fastapi import Depends, Header

from sqlalchemy.ext.asyncio import AsyncSession

from ..config_data.logger_config import logger
from ..database import ManagerTweets, get_session, Tweets, ManagerMedia
from ..schemas import schemas as schema
from ..utils.auth import check_auth


def register_tweet_routes(app):
    @app.delete(
        "/api/tweets/{id}",
        status_code=200,
        tags=["tweet"],
        response_model=schema.ServerBoolAnswer,
        summary="Удаление твита",
    )
    async def rout_delete_tweet(
        id: int,
        api_key: str = Header(..., description="API-ключ пользователя"),
        session: AsyncSession = Depends(get_session),
    ):
        """Удаление твита"""
        logger.debug("Удаление твита")

        await check_auth(session, api_key)

        object_tweet = await ManagerTweets.get_by_id(session, id)

        await session.delete(object_tweet)

        return schema.ServerBoolAnswer()

    @app.get(
        "/api/tweets",
        status_code=200,
        tags=["tweet"],
        response_model=schema.TweetTotalResponse,
        summary="Получение всех твитов",
    )
    async def rout_get_tweets(
        api_key: str = Header(..., description="API-ключ пользователя"),
        session: AsyncSession = Depends(get_session),
    ):
        """Получение всех твитов"""
        logger.debug("Получение всех твитов")

        await check_auth(session, api_key)

        total_object_tweets = await ManagerTweets.get_all(session)

        if not total_object_tweets:
            return schema.TweetTotalResponse(
                result="true",
                tweets=[],
            )

        return schema.TweetTotalResponse(
            tweets=[
                schema.TweetsData(
                    id=tweet.tweet_id,
                    content=tweet.content,
                    attachments=[media.file_path for media in tweet.media],
                    author=schema.User(id=tweet.author.user_id, name=tweet.author.name),
                    likes=[
                        schema.Like(
                            user_id=like.user.user_id,
                            name=like.user.name,
                        )
                        for like in tweet.likes
                    ],
                )
                for tweet in total_object_tweets
            ]
        )

    @app.post(
        "/api/tweets",
        status_code=201,
        response_model=schema.TweetResponse,
        tags=["tweet"],
        summary="Создание нового твита",
    )
    async def rout_create_tweet(
        tweet: schema.TweetCreate,
        api_key: str = Header(..., description="API-ключ пользователя"),
        session: AsyncSession = Depends(get_session),
    ) -> schema.TweetResponse:
        """Создание нового твита"""
        logger.debug("Создание нового твита")

        user = await check_auth(session, api_key)

        new_tweet = Tweets(content=tweet.tweet_data, author_id=user.user_id)

        if tweet.tweet_media_ids:
            for media_id in tweet.tweet_media_ids:
                media_objects = await ManagerMedia.get_by_id(session, media_id)
                new_tweet.media.append(media_objects)

        session.add(new_tweet)
        await session.flush()

        return schema.TweetResponse(
            tweet_id=new_tweet.tweet_id,
            created_at=new_tweet.created_at,
        )
