from typing import List

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
            raise HTTPException(status_code=404, detail="Tweet not found")

        return obj

    @classmethod
    async def get_all(cls, session: AsyncSession) -> List[Tweets]:
        """Получение всех твитов"""
        result = await session.execute(
            select(Tweets).options(
                selectinload(Tweets.author),
                selectinload(Tweets.likes),
                selectinload(Tweets.media),
            )
        )

        return list(result.unique().scalars().all())


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
            raise HTTPException(status_code=404, detail="User not found")

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
            raise HTTPException(status_code=404, detail="User not found")

        return obj

    @classmethod
    def check_subscribe_yourself(
        cls, session: AsyncSession, user_id: int, follow_id: int
    ) -> None:

        if user_id == follow_id:
            raise HTTPException(
                status_code=409, detail="Conflict subscribe to yourself"
            )

    @classmethod
    def check_exists_following(
        cls, session: AsyncSession, user: User, object_user: int
    ) -> None:
        """Проверка наличия подписки"""
        if object_user in user.following:
            raise HTTPException(status_code=409, detail="Already subscribe")

    @classmethod
    def check_empty_following(
        cls, session: AsyncSession, user: User, object_user: int
    ) -> None:
        """Проверка отсутствия подписки"""
        if object_user not in user.following:
            raise HTTPException(status_code=409, detail="Not subscribe")


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
            raise HTTPException(status_code=404, detail="Like not found")

        return obj


class ManagerMedia:

    @classmethod
    async def get_by_id(cls, session: AsyncSession, media_id: int) -> Media:
        """Получение медиа по его id"""
        result = await session.execute(select(Media).where(Media.media_id == media_id))
        obj = result.scalar_one_or_none()

        if not obj:
            raise HTTPException(status_code=404, detail="Media not found")

        return obj
