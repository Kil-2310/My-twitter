import pytest
from .factories import UserFactory, TweetsFactory, MediaFactory
from sqlalchemy import select
from backend.app.database.models import Tweets, User


# Общие фикстуры


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


@pytest.fixture
async def test_tweet_1(db_session):
    """Создание 1 твита перед каждым тестом"""
    tweet = TweetsFactory.build()
    db_session.add(tweet)
    await db_session.commit()
    await db_session.refresh(tweet)
    return tweet


@pytest.fixture
async def test_media_1(db_session):
    """Создание медиа"""
    media = MediaFactory.build()
    db_session.add(media)
    await db_session.commit()
    await db_session.refresh(media)
    return media


# Сами тесты


async def test_create_user(db_session):
    """Создание пользователя"""
    user = UserFactory.build()

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.user_id is not None
    assert user.name is not None
    assert user.created_at is not None


async def test_create_tweet(db_session):
    """Создание твита"""
    tweet = TweetsFactory.build()

    db_session.add(tweet)
    await db_session.commit()
    await db_session.refresh(tweet)

    assert tweet.tweet_id is not None

async def test_get_tweets_default_0(db_session):
    """Получение всех твитов из БД"""
    result = await db_session.execute(
        select(Tweets)
    )
    tweets = result.scalars().all()

    assert len(tweets) == 0


async def test_get_tweets_default_1(db_session, test_tweet_1):
    """Получение всех твитов из БД"""
    result = await db_session.execute(
        select(Tweets)
    )
    tweets = result.scalars().all()

    assert len(tweets) == 1


async def test_delete_tweet(db_session, test_tweet_1):
    """Удаление твита"""
    await db_session.delete(test_tweet_1)

    result = await db_session.execute(
        select(Tweets)
    )
    tweets = result.scalars().all()

    assert len(tweets) == 0


async def test_create_media(db_session):
    """Создание медиа"""
    media = MediaFactory.build()

    db_session.add(media)
    await db_session.commit()
    await db_session.refresh(media)

    assert media.media_id is not None


async def test_tweet_media(db_session, test_media_1, test_tweet_1):
    """Создание твита и првязка к нему медиа"""
    test_tweet_1.media.append(test_media_1)
    await db_session.commit()

    await db_session.refresh(test_tweet_1)
    await db_session.refresh(test_media_1)

    assert test_media_1 in test_tweet_1.media


async def test_follow(db_session, test_user_1, test_user_2):
    """Тест подписки"""
    test_user_1.following.append(test_user_2)
    await db_session.commit()

    await db_session.refresh(test_user_1)
    await db_session.refresh(test_user_2)

    assert test_user_2 in test_user_1.following
    assert test_user_1 in test_user_2.followers


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


async def test_get_my_profile(db_session, test_user_1):
    """Получение профиля пользователя"""
    result = await db_session.execute(
        select(User).where(User.user_id == test_user_1.user_id)
    )

    user = result.scalars().one()

    assert user.user_id == test_user_1.user_id
    assert user.name == test_user_1.name
