from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel


class Tweet(BaseModel):
    content: str
    tweet_media_ids: Optional[List[int]] = []


class TweetIn(Tweet):
    pass


class TweetOut(Tweet):
    tweet_id: int
    author_id: int
    result: bool = True
    created_at: datetime

    model_config = {"from_attributes": True}


class Media(BaseModel, AbstractMedia):
    pass


class MediaIn(Media):
    pass


class MediaOut(Media):
    result: bool = True
    uploaded_by: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ServerBoolAnswer(BaseModel):
    result: str


class User(BaseModel):
    user_id: int
    name: str


class UserProfile(BaseModel):
    followers: List[User]
    following: List[User]


class UserProfileResponse(BaseModel):
    result: ServerBoolAnswer
    user: UserProfile

class Author(BaseModel):
    id: int
    name: str

class Like(BaseModel):
    user_id: int
    name: str


class TweetsData(BaseModel):
    tweet_id: int
    content: str
    attachments: Optional[List[str]] = []
    author: Author
    likes: List[Like] = []

class TweetTotalResponse(BaseModel):
    result: ServerBoolAnswer
    tweets: List[TweetsData]

