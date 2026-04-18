from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from ..config_data.logger_config import logger
from ..database import ManagerUser, get_session
from ..schemas import schemas as schema
from ..utils.auth import check_auth


def register_user_routes(app):
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
        session: AsyncSession = Depends(get_session),
    ):
        """Подписка на пользователя"""
        logger.debug("Подписка на пользователя")

        user = await check_auth(session, api_key)

        object_user = await ManagerUser.get_by_id(session, id)

        await ManagerUser.get_by_id(session, object_user.user_id)

        ManagerUser.check_subscribe_yourself(user.user_id, object_user.user_id)

        ManagerUser.check_exists_following(user, object_user)

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
        session: AsyncSession = Depends(get_session),
    ):
        """Отписка от пользователя"""
        logger.debug("Отписка от пользователя")

        user = await check_auth(session, api_key)

        object_user = await ManagerUser.get_by_id(session, id)

        await ManagerUser.get_by_id(session, object_user.user_id)

        ManagerUser.check_empty_following(user, object_user)

        user.following.remove(object_user)

        return schema.ServerBoolAnswer()

    @app.get(
        "/api/users/me",
        status_code=200,
        tags=["user"],
        response_model=schema.UserProfileResponse,
        summary="Получение данных профиля пользователя",
    )
    async def route_get_me(
        api_key: str = Header(..., description="API-ключ пользователя"),
        session: AsyncSession = Depends(get_session),
    ):
        """Получение данных профиля пользователя"""
        logger.debug("Получение данных профиля пользователя")

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
        summary="Получение данных стороннего профиля пользователя по id",
    )
    async def route_get_user(
        id: int,
        api_key: str = Header(..., description="API-ключ пользователя"),
        session: AsyncSession = Depends(get_session),
    ):
        """Получение данных стороннего профиля пользователя по id"""
        logger.debug("Получение данных стороннего профиля пользователя по id")

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
