import pytest
from sqlalchemy import select

from backend.tests.factories import UserFactory


@pytest.mark.asyncio
async def test_create_client_with_factory(db_session):
    """Тест создания клиента через фабрику"""
    # Создаем пользователя (синхронно)
    user = UserFactory.build()  # build() создает объект без сохранения
    
    # Добавляем в сессию и сохраняем асинхронно
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Проверяем, что пользователь создался
    assert user.user_id is not None
    assert user.name is not None
    assert user.created_at is not None