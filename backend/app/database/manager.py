from typing import List

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..config_data.logger_config import logger
from .models import Likes, Media, Tweets, User


class ManagerTweets:

    @classmethod
    async def get_by_id(cls, session: AsyncSession, tweet_id: int) -> Tweets:
        """Получение твита по id"""
        result = await session.execute(
            select(Tweets).where(Tweets.tweet_id == tweet_id)
        )
        obj = result.scalar_one_or_none()

        if not obj:
            logger.error("Твит {} не найден".format(tweet_id))
            raise HTTPException(
                status_code=404,
                detail={
                    "result": False,
                    "error_type": "not_found",
                    "error_message": "Tweet not found",
                },
            )

        return obj

    @classmethod
    async def get_all(cls, session: AsyncSession) -> List[Tweets]:
        """Получение всех твитов"""
        result = await session.execute(
            select(Tweets).options(
                selectinload(Tweets.author),
                selectinload(Tweets.likes).selectinload(Likes.user),
                selectinload(Tweets.media),
            )
        )
        objs = list(result.unique().scalars().all())
        logger.info("Получено {} твитов".format(len(objs)))

        return objs


class ManagerUser:

    @classmethod
    async def get_by_api_key(cls, session: AsyncSession, api_key: str) -> User:
        """Получение пользователя по api key"""
        result = await session.execute(
            select(User)
            .where(User.api_key == api_key)
            .options(selectinload(User.following), selectinload(User.followers))
        )
        obj = result.scalar_one_or_none()

        if not obj:
            logger.error("Пользователь с api_key {} не найден".format(api_key))
            raise HTTPException(
                status_code=404,
                detail={
                    "result": False,
                    "error_type": "not_found",
                    "error_message": "User not found",
                },
            )

        logger.info("Пользователь {} авторизован".format(obj.name))
        return obj

    @classmethod
    async def get_by_id(cls, session: AsyncSession, user_id: int) -> User:
        """Получение пользователя по id"""
        result = await session.execute(
            select(User)
            .where(User.user_id == user_id)
            .options(selectinload(User.following), selectinload(User.followers))
        )
        obj = result.scalar_one_or_none()

        if not obj:
            logger.error("Пользователь {} не найден".format(user_id))
            raise HTTPException(
                status_code=404,
                detail={
                    "result": False,
                    "error_type": "not_found",
                    "error_message": "User not found",
                },
            )

        return obj

    @classmethod
    def check_subscribe_yourself(cls, user_id: int, follow_id: int) -> None:
        """Проверка подписки на себя"""
        if user_id == follow_id:
            logger.error("Попытка подписаться на себя user_id={}".format(user_id))
            raise HTTPException(
                status_code=409,
                detail={
                    "result": False,
                    "error_type": "conflict",
                    "error_message": "Cannot subscribe to yourself",
                },
            )

    @classmethod
    def check_exists_following(cls, user: User, target_user_id: int) -> None:
        """Проверка наличия подписки"""
        following_ids = [f.user_id for f in user.following]
        if target_user_id in following_ids:
            logger.error(
                "Подписка уже существует user={} follow={}".format(
                    user.user_id, target_user_id
                )
            )
            raise HTTPException(
                status_code=409,
                detail={
                    "result": False,
                    "error_type": "conflict",
                    "error_message": "Already subscribed",
                },
            )

    @classmethod
    def check_empty_following(cls, user: User, target_user_id: int) -> None:
        """Проверка отсутствия подписки"""
        following_ids = [f.user_id for f in user.following]
        if target_user_id not in following_ids:
            logger.error(
                "Подписка не найдена user={} follow={}".format(
                    user.user_id, target_user_id
                )
            )
            raise HTTPException(
                status_code=409,
                detail={
                    "result": False,
                    "error_type": "conflict",
                    "error_message": "Not subscribed",
                },
            )


class ManagerLikes:

    @classmethod
    async def get_by_user_id_and_tweet_id(
        cls, session: AsyncSession, user_id: int, tweet_id: int
    ) -> Likes:
        """Получение модели like по id пользователя и твиту"""
        result = await session.execute(
            select(Likes).where(Likes.user_id == user_id, Likes.tweet_id == tweet_id)
        )
        obj = result.scalar_one_or_none()

        if not obj:
            logger.error("Лайк не найден user={} tweet={}".format(user_id, tweet_id))
            raise HTTPException(
                status_code=404,
                detail={
                    "result": False,
                    "error_type": "not_found",
                    "error_message": "Like not found",
                },
            )

        return obj


class ManagerMedia:

    @classmethod
    async def get_by_id(cls, session: AsyncSession, media_id: int) -> Media:
        """Получение медиа по его id"""
        result = await session.execute(select(Media).where(Media.media_id == media_id))
        obj = result.scalar_one_or_none()

        if not obj:
            logger.error("Медиа {} не найдено".format(media_id))
            raise HTTPException(
                status_code=404,
                detail={
                    "result": False,
                    "error_type": "not_found",
                    "error_message": "Media not found",
                },
            )

        return obj
