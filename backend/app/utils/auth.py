from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import ManagerUser, User


async def check_auth(session: AsyncSession, api_key: str) -> User:
    """Проверка api key и проверка наличия пользователя в БД"""
    if not api_key:
        raise HTTPException(status_code=401, detail="API key is required")

    return await ManagerUser.get_by_api_key(session, api_key)
