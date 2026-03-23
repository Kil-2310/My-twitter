from .database import Base

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)

# from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(100), nullable=False)
    api_key = Column(String(255), nullable=True, unique=True)
    created_at = Column(DateTime, nullable=False)

    # # Пользователи, на которых я подписан (мои following)
    # following = relationship(
    #     'Follows',
    #     foreign_keys='Follows.follower_id',
    #     back_populates='follower'
    # )

    # # Мои подписчики
    # followers = relationship(
    #     'Follows',
    #     foreign_keys='Follows.following_id',
    #     back_populates='following'
    # )


class Follows(Base):
    __tablename__ = "follows"

    __table_args__ = (
        UniqueConstraint("following_id", "follower_id", name="unique_follow"),
    )

    follows_id = Column(Integer, autoincrement=True, primary_key=True)
    following_id = Column(Integer, ForeignKey("user.user_id"))
    follower_id = Column(Integer, ForeignKey("user.user_id"))
    created_at = Column(DateTime, nullable=False)

    # follower = relationship('User', foreign_keys=[follower_id], back_populates='following')
    # following = relationship('User', foreign_keys=[following_id], back_populates='followers')


class Media(Base):
    __tablename__ = "media"

    media_id = Column(Integer, autoincrement=True, primary_key=True)
    file_name = Column(String(50), nullable=False)
    file_path = Column(String(100), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("user.user_id"))
    created_at = Column(DateTime, nullable=False)


class Tweets(Base):
    __tablename__ = "tweets"

    tweet_id = Column(Integer, autoincrement=True, primary_key=True)
    content = Column(String(255), nullable=False)
    author_id = Column(Integer, ForeignKey("user.user_id"))
    created_at = Column(DateTime, nullable=False)


class TweetMedia(Base):
    __tablename__ = "tweet_media"

    __table_args__ = (
        UniqueConstraint("tweet_id", "media_id", name="unique_tweet_media"),
    )

    tweet_media_id = Column(Integer, autoincrement=True, primary_key=True)
    tweet_id = Column(Integer, ForeignKey("tweets.tweet_id"))
    media_id = Column(Integer, ForeignKey("media.media_id"))


class Likes(Base):
    __tablename__ = "likes"

    __table_args__ = (UniqueConstraint("tweet_id", "user_id", name="unique_likes"),)

    like_id = Column(Integer, autoincrement=True, primary_key=True)
    tweet_id = Column(Integer, ForeignKey("tweets.tweet_id"))
    user_id = Column(Integer, ForeignKey("user.user_id"))
    created_at = Column(DateTime, nullable=False)
