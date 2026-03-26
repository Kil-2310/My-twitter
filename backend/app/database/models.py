from .database import Base

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from sqlalchemy.orm import relationship

from datetime import datetime


class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(100), nullable=False)
    api_key = Column(String(255), unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    # кого я читаю
    following = relationship(
        "User",
        secondary="follows",
        primaryjoin="User.user_id == Follows.follower_id",
        secondaryjoin="User.user_id == Follows.following_id",
        back_populates="followers",
        lazy="selectin",
        cascade="save-update",
    )

    # кто читает меня
    followers = relationship(
        "User",
        secondary="follows",
        primaryjoin="User.user_id == Follows.following_id",
        secondaryjoin="User.user_id == Follows.follower_id",
        back_populates="following",
        lazy="selectin",
        cascade="save-update",
    )

    likes = relationship(
        "Likes",
        back_populates="user",
        lazy="selectin",
        cascade="save-update, delete-orphan",
    )

    media = relationship(
        "Media", back_populates="uploader", lazy="selectin", cascade="save-update"
    )

    tweets = relationship(
        "Tweets", back_populates="author", lazy="selectin", cascade="save-update"
    )


class Follows(Base):
    __tablename__ = "follows"

    follower_id = Column(Integer, ForeignKey("user.user_id"), primary_key=True)
    following_id = Column(Integer, ForeignKey("user.user_id"), primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)


class Media(Base):
    __tablename__ = "media"

    media_id = Column(Integer, autoincrement=True, primary_key=True)
    file_name = Column(String(50), nullable=False)
    file_path = Column(String(100), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("user.user_id"))
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    uploader = relationship(
        "User", back_populates="media", lazy="select", cascade="save-update"
    )

    tweets = relationship(
        "Tweets",
        secondary="tweet_media",
        back_populates="media",
        lazy="selectin",
        cascade="save-update",
    )


class Tweets(Base):
    __tablename__ = "tweets"

    tweet_id = Column(Integer, autoincrement=True, primary_key=True)
    content = Column(String(255), nullable=False)
    author_id = Column(Integer, ForeignKey("user.user_id"))
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    author = relationship(
        "User", back_populates="tweets", lazy="select", cascade="save-update"
    )
    media = relationship(
        "Media",
        secondary="tweet_media",
        back_populates="tweets",
        lazy="selectin",
        cascade="save-update",
    )

    likes = relationship(
        "Likes", back_populates="tweet", lazy="selectin", cascade="all, delete-orphan"
    )


class TweetMedia(Base):
    __tablename__ = "tweet_media"

    tweet_id = Column(Integer, ForeignKey("tweets.tweet_id"), primary_key=True)
    media_id = Column(Integer, ForeignKey("media.media_id"), primary_key=True)


class Likes(Base):
    __tablename__ = "likes"

    tweet_id = Column(Integer, ForeignKey("tweets.tweet_id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.now)

    tweet = relationship("Tweets", back_populates="likes")
    user = relationship("User", back_populates="likes")
