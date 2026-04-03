import os
import uuid
from pathlib import Path

import aiofiles
from fastapi import FastAPI, File, UploadFile, Header
from sqlalchemy import select

from ..config_data.logger_config import logger
from ..database import (
    Base,
    Likes,
    ManagerLikes,
    ManagerMedia,
    ManagerTweets,
    ManagerUser,
    Media,
    Tweets,
    User,
    async_session,
    engine,
)
from ..schemas import schemas as schema
from ..utils import check_auth


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
                await session.commit()
                logger.debug("Добавлено {} пользователей", len(object_users))

        logger.debug("В базе уже есть пользователи")

    @app.on_event("shutdown")
    async def shutdown():
        await async_session.close()
        await engine.dispose()
        logger.debug("Сессия завершена")

    # === Основная логика ===

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
    ) -> schema.TweetResponse:
        """Создание нового твита"""
        async with async_session() as session:
            async with session.begin():
                user = await check_auth(session, api_key)

                new_tweet = Tweets(content=tweet.tweet_data, author_id=user.user_id)

                if tweet.tweet_media_ids:
                    for media_id in tweet.tweet_media_ids:

                        media_objects = await ManagerMedia.get_by_id(session, media_id)

                        new_tweet.media.append(media_objects)

                session.add(new_tweet)

        return schema.TweetResponse(
            tweet_id=new_tweet.tweet_id,
            created_at=new_tweet.created_at,
        )

    @app.post(
        "/api/medias",
        status_code=201,
        response_model=schema.MediaResponse,
        tags=["media"],
        summary="Создание медиа через загрузку файла",
    )
    async def rout_create_media(
        api_key: str = Header(..., description="API-ключ пользователя"),
        file: UploadFile = File(..., description="Выберете медиафайл для загрузки"),
    ) -> schema.MediaResponse:
        """Создание нового медиа"""
        async with async_session() as session:
            user = await check_auth(session, api_key)

        current_file_path = Path(__file__).parent
        UPLOAD_DIR = current_file_path / "uploads"
        UPLOAD_DIR.mkdir(exist_ok=True)

        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename

        try:
            async with aiofiles.open(file_path, "wb") as out_file:
                content = await file.read()
                await out_file.write(content)

            async with async_session() as session:
                async with session.begin():

                    new_media = Media(
                        file_name=file.filename,
                        file_path=str(file_path),
                        uploaded_by=user.user_id,
                    )

                    session.add(new_media)

            return schema.MediaResponse(
                uploaded_by=new_media.uploaded_by,
                media_id=new_media.media_id,
            )

        except Exception:
            # Удаление медиа
            if file_path.exists():
                file_path.unlink()

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
    ):
        """Удаление твита"""
        async with async_session() as session:
            async with session.begin():
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
    ):
        """Получение всех твитов"""
        async with async_session() as session:
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
        "/api/tweets/{id}/likes",
        status_code=201,
        tags=["likes"],
        response_model=schema.ServerBoolAnswer,
        summary="Поставить лайк на твит",
    )
    async def rout_create_like_tweet(
        id: int,
        api_key: str = Header(..., description="API-ключ пользователя"),
    ):
        """Создание лайка"""
        async with async_session() as session:
            async with session.begin():
                user = await check_auth(session, api_key)

                object_tweet = await ManagerTweets.get_by_id(session, id)

                new_like = Likes()

                session.add(new_like)

                user.likes.append(new_like)
                object_tweet.likes.append(new_like)

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
    ):
        """Удаление лайка"""
        async with async_session() as session:
            async with session.begin():
                user = await check_auth(session, api_key)

                object_tweet = await ManagerTweets.get_by_id(session, id)

                object_likes = await ManagerLikes.get_by_user_id_and_tweet_id(
                    session, user.user_id, object_tweet.tweet_id
                )

                await session.delete(object_likes)

        return schema.ServerBoolAnswer()

    @app.post(
        "/api/users/{id}/follow",
        status_code=201,
        tags=["user"],
        response_model=schema.ServerBoolAnswer,
        summary="Подписаться на пользователя",
    )
    async def rout_create_follow(
        id: int,
        api_key: str = Header(..., description="API-ключ пользователя"),
    ):
        """Подписка на пользователя"""
        async with async_session() as session:
            async with session.begin():
                user = await check_auth(session, api_key)

                object_user = await ManagerUser.get_by_id(session, id)

                await ManagerUser.get_by_id(session, object_user.user_id)

                ManagerUser.check_subscribe_yourself(
                    session, user.user_id, object_user.user_id
                )

                ManagerUser.check_exists_following(session, user, object_user)

                user.following.append(object_user)

        return schema.ServerBoolAnswer()

    @app.delete(
        "/api/users/{id}/follow",
        status_code=200,
        tags=["user"],
        response_model=schema.ServerBoolAnswer,
        summary="Отписка от пользователя",
    )
    async def rout_delete_follow(
        id: int,
        api_key: str = Header(..., description="API-ключ пользователя"),
    ):
        """Отписка от пользователя"""
        async with async_session() as session:
            async with session.begin():
                user = await check_auth(session, api_key)

                object_user = await ManagerUser.get_by_id(session, id)

                await ManagerUser.get_by_id(session, object_user.user_id)

                ManagerUser.check_empty_following(session, user, object_user)

                user.following.remove(object_user)

        return schema.ServerBoolAnswer()

    @app.get(
        "/api/users/me",
        status_code=200,
        tags=["user"],
        response_model=schema.UserProfileResponse,
        summary="Получение данных профиля",
    )
    async def route_get_me(
        api_key: str = Header(..., description="API-ключ пользователя"),
    ):
        """Получение данных профиля"""
        async with async_session() as session:
            user = await check_auth(session, api_key)

            return schema.UserProfileResponse(
                user=schema.UserProfile(
                    id=user.user_id,
                    name=user.name,
                    followers=[
                        schema.User(id=f.user_id, name=f.name) for f in user.followers
                    ],
                    following=[
                        schema.User(id=f.user_id, name=f.name) for f in user.following
                    ],
                ),
            )

    @app.get(
        "/api/users/{id}",
        status_code=200,
        tags=["user"],
        response_model=schema.UserProfileResponse,
        summary="Получение данных стороннего пользователя",
    )
    async def route_get_user(
        id: int,
        api_key: str = Header(..., description="API-ключ пользователя"),
    ):
        """Получение данных стороннего пользователя"""
        async with async_session() as session:
            await check_auth(session, api_key)

            user_object = await ManagerUser.get_by_id(session, id)

            return schema.UserProfileResponse(
                user=schema.UserProfile(
                    id=user_object.user_id,
                    name=user_object.name,
                    followers=[
                        schema.User(id=f.user_id, name=f.name)
                        for f in user_object.followers
                    ],
                    following=[
                        schema.User(id=f.user_id, name=f.name)
                        for f in user_object.following
                    ],
                ),
            )

    return app
