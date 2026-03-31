import pytest
from backend.tests.factories import UserFactory


@pytest.fixture
async def test_user_1(db_session):
    """Создание 1 пользователя перед каждым тестом"""
    user = UserFactory.build()
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_user_2(db_session):
    """Создание 2 пользователя перед каждым тестом"""
    user = UserFactory.build()
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_follow(db_session, test_user_1, test_user_2):
    """Тест подписки"""
    test_user_1.following.append(test_user_2)
    await db_session.commit()

    await db_session.refresh(test_user_1)
    await db_session.refresh(test_user_2)

    assert test_user_2 in test_user_1.following
    assert test_user_1 in test_user_2.followers


@pytest.mark.asyncio
async def test_unfollow(db_session, test_user_1, test_user_2):
    """Тест отписки"""
    test_user_1.following.append(test_user_2)
    await db_session.commit()

    await db_session.refresh(test_user_1)
    assert test_user_2 in test_user_1.following

    test_user_1.following.remove(test_user_2)
    await db_session.commit()

    await db_session.refresh(test_user_1)
    await db_session.refresh(test_user_2)

    assert test_user_2 not in test_user_1.following
    assert test_user_1 not in test_user_2.followers
    assert len(test_user_1.following) == 0
    assert len(test_user_2.followers) == 0


@pytest.mark.asyncio
async def test_create_client_with_factory(db_session):
    """Создание пользователя"""
    user = UserFactory.build()

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.user_id is not None
    assert user.name is not None
    assert user.created_at is not None
