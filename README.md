# My-Twitter

Корпоративный сервис микроблогов с базовым функционалом для внутреннего использования.

## Цель проекта

Реализовать бэкенд сервиса микроблогов для корпоративной сети с урезанным функционалом, обеспечивающим основные потребности в обмене короткими сообщениями.

# Технологии

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, Alembic
- **Database**: PostgreSQL (production), SQLite (development)
- **Контейнеризация**: Docker, Docker Compose
- **Веб-сервер**: Nginx (reverse proxy)
- **Хранение файлов**: Local storage (с возможностью расширения до S3)

# Запуск всех сервисов
docker compose up

# Остановка контейнеров
docker compose down

# Таблицы Базы данных

1. Таблица пользователей
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    api_key VARCHAR(64) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

2. Таблица подписок (followers/following)
-- связь many-to-many между пользователями
CREATE TABLE follows (
    follower_id INT NOT NULL,
    following_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (follower_id, following_id),
    FOREIGN KEY (follower_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (following_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CHECK (follower_id != following_id)
);

3. Таблица медиа-файлов
CREATE TABLE media (
    media_id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    uploaded_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploaded_by) REFERENCES users(user_id) ON DELETE CASCADE
);

4. Таблица твитов
CREATE TABLE tweets (
    tweet_id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    author_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(user_id) ON DELETE CASCADE
);

5. Таблица связей твитов с медиа (many-to-many)
CREATE TABLE tweet_media (
    tweet_id INT NOT NULL,
    media_id INT NOT NULL,
    PRIMARY KEY (tweet_id, media_id),
    FOREIGN KEY (tweet_id) REFERENCES tweets(tweet_id) ON DELETE CASCADE,
    FOREIGN KEY (media_id) REFERENCES media(media_id) ON DELETE CASCADE
);

6. Таблица лайков
CREATE TABLE likes (
    tweet_id INT NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (tweet_id, user_id),
    FOREIGN KEY (tweet_id) REFERENCES tweets(tweet_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

# Контракт API

1.
POST /api/tweets
HTTP-Params:
    api-key: str
{
    “tweet_data”: string
    “tweet_media_ids”: Array[int] // Опциональный параметр. Загрузка
    картинок будет происходить по endpoint /api/media. Фронтенд будет
    подгружать картинки туда автоматически при отправке твита и подставлять
    id оттуда в json.
}
Запросом на этот endpoint пользователь будет создавать новый твит.
Бэкенд будет его валидировать и сохранять в базу.
В ответ должен вернуться id созданного твита.
{
    “result”: true,
    “tweet_id”: int
}

2.
Endpoint для загрузки файлов из твита. Загрузка происходит через
отправку формы.
POST /api/medias
HTTP-Params:
    api-key: str
form: file=”image.jpg”
В ответ должен вернуться id загруженного файла.
{
    “result”: true,
    “media_id”: int
}

3.
Ещё нам потребуется endpoint по удалению твита. В этом endpoint мы
должны убедиться, что пользователь удаляет именно свой собственный твит.
DELETE /api/tweets/<id>
HTTP-Params:
    api-key: str
В ответ должно вернуться сообщение о статусе операции.
{
    “result”: true
}

Пользователь может поставить отметку «Нравится» на твит.
POST /api/tweets/<id>/likes
HTTP-Params:
    api-key: str
В ответ должно вернуться сообщение о статусе операции.
{
    “result”: true
}

4.
Пользователь может убрать отметку «Нравится» с твита.
DELETE /api/tweets/<id>/likes
HTTP-Params:
    api-key: str
В ответ должно вернуться сообщение о статусе операции.
{
    “result”: true
}

5.
Пользователь может зафоловить другого пользователя.
POST /api/users/<id>/follow
HTTP-Params:
    api-key: str
В ответ должно вернуться сообщение о статусе операции.
{
    “result”: true
}

6.
Пользователь может убрать подписку на другого пользователя.
DELETE /api/users/<id>/follow
HTTP-Params:
    api-key: str
В ответ должно вернуться сообщение о статусе операции.
{
    “result”: true
}

7.
Пользователь может получить ленту с твитами.
GET /api/tweets
HTTP-Params:
    api-key: str
В ответ должен вернуться json со списком твитов для ленты этого
пользователя.
{
    “result”: true,
    "tweets": [
        {
            "id": int,
            "content": string,
            "attachments" [
                link_1, // relative?
                link_2,
                ...
            ]
            "author": {
                "id": int
                "name": string
            }
            “likes”: [
                {
                    “user_id”: int,
                    “name”: string
                }
            ]
        },
        ...,
    ]
}

В случае любой ошибки на стороне бэкенда возвращайте сообщение
следующего формата:
{
    “result”: false,
    “error_type”: str,
    “error_message”: str
}

8.
Пользователь может получить информацию о своём профиле:
GET /api/users/me
HTTP-Params:
    api-key: str
В ответ получаем:
{
    "result":"true",
    "user":{
        "id":"int",
        "name":"str",
        "followers":[
            {
                "id":"int",
                "name":"str"
            }
        ],
        "following":[
            {
                "id":"int",
                "name":"str"
            }
        ]
    }
}

9.
Пользователь может получить информацию о произвольном профиле по его
id:
GET /api/users/<id>
В ответ получаем:
{
    "result":"true",
    "user":{
        "id":"int",
        "name":"str",
        "followers":[
            {
                "id":"int",
                "name":"str"
            }
        ],
        "following":[
            {
                "id":"int",
                "name":"str"
            }
        ]
    }
}