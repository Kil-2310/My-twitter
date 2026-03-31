from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

# Общие модели


class ServerBoolAnswer(BaseModel):
    result: str = "true"


# Модели User


class User(BaseModel):
    """Базовая модель пользователя"""

    id: int
    name: str


class UserProfile(BaseModel):
    """Подписчики и подписки пользователя"""

    id: int
    name: str
    followers: List[User]
    following: List[User]


class UserProfileResponse(BaseModel):
    """Ответа API с информацией о пользователе"""

    result: str = "true"
    user: UserProfile

    model_config = {"from_attributes": True}


# Модели Likes


class Like(BaseModel):
    """Базовая модель лайка"""

    user_id: int
    name: str


# Модели Tweet


class TweetCreate(BaseModel):
    """Создание твита"""

    content: str
    tweet_media_ids: Optional[List[int]] = []


class TweetResponse(BaseModel):
    """Ответа API после создания твита"""

    result: str = "true"
    tweet_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class TweetsData(BaseModel):
    """Информация о конкретном твите"""

    tweet_id: int
    content: str
    attachments: Optional[List[str]] = []
    author: User
    likes: List[Like] = []


class TweetTotalResponse(BaseModel):
    """Ответа API со всеми твитами всех пользователей"""

    result: str = "true"
    tweets: List[TweetsData]

    class Config:
        orm_mode = True


# Модели Media


class MediaResponse(BaseModel):
    """Ответа API после создания медиа"""

    result: str = "true"
    uploaded_by: int
    media_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
