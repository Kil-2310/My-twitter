import random
from datetime import datetime, timedelta

import factory

from backend.app.database.models import User, Follows, Media, Tweets, TweetMedia, Likes


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"

    user_id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    api_key = factory.LazyAttribute(
        lambda obj: f"api_key_{obj.name.replace(' ', '_').lower()}_{random.randint(1000, 9999)}"
    )
    created_at = factory.LazyFunction(
        lambda: datetime.now() - timedelta(days=random.randint(0, 365))
    )


class FollowsFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Follows
        sqlalchemy_session_persistence = "commit"

    follows_id = factory.Sequence(lambda n: n)
    following_id = factory.SubFactory(UserFactory)
    follower_id = factory.SubFactory(UserFactory)
    created_at = factory.LazyFunction(
        lambda: datetime.now() - timedelta(days=random.randint(0, 180))
    )


class MediaFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Media
        sqlalchemy_session_persistence = "commit"

    media_id = factory.Sequence(lambda n: n)
    file_name = factory.LazyAttribute(
        lambda obj: f"{factory.Faker('word').generate()}_{random.randint(1000, 9999)}.{random.choice(['jpg', 'png', 'gif', 'mp4'])}"
    )
    file_path = factory.LazyAttribute(lambda obj: f"/uploads/{obj.file_name}")
    uploaded_by = factory.SubFactory(UserFactory)
    created_at = factory.LazyFunction(
        lambda: datetime.now() - timedelta(days=random.randint(0, 60))
    )


class TweetsFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Tweets
        sqlalchemy_session_persistence = "commit"

    tweet_id = factory.Sequence(lambda n: n)
    content = factory.Faker("text", max_nb_chars=280)
    author_id = factory.SubFactory(UserFactory)
    created_at = factory.LazyFunction(
        lambda: datetime.now()
        - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
    )


class TweetMediaFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = TweetMedia
        sqlalchemy_session_persistence = "commit"

    tweet_media_id = factory.Sequence(lambda n: n)
    tweet_id = factory.SubFactory(TweetsFactory)
    media_id = factory.SubFactory(MediaFactory)


class LikesFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Likes
        sqlalchemy_session_persistence = "commit"

    like_id = factory.Sequence(lambda n: n)
    tweet_id = factory.SubFactory(TweetsFactory)
    user_id = factory.SubFactory(UserFactory)
    created_at = factory.LazyFunction(
        lambda: datetime.now() - timedelta(days=random.randint(0, 60))
    )
