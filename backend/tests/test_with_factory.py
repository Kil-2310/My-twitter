import pytest

from backend.tests.factories import UserFactory


@pytest.mark.asyncio
async def test_create_client_with_factory(db_session):
    """Создание клиента"""
    user = UserFactory.build()

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.user_id is not None
    assert user.name is not None
    assert user.created_at is not None