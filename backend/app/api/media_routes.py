import os
import uuid
from pathlib import Path

import aiofiles
from fastapi import Depends, File, UploadFile, Header
from sqlalchemy.ext.asyncio import AsyncSession

from ..config_data.logger_config import logger
from ..database import Media, get_session
from ..schemas import schemas as schema
from ..utils.auth import check_auth

def register_media_routes(app):
    @app.post(
        "/api/medias",
        status_code=201,
        response_model=schema.MediaResponse,
        tags=["media"],
        summary="Создание медиа через загрузку файла",
    )
    async def rout_create_media(
        api_key: str = Header(..., description="API-ключ пользователя"),
        file: UploadFile = File(..., description="Выберете медиафайл для загрузки"),
        session: AsyncSession = Depends(get_session),
    ) -> schema.MediaResponse:
        """Создание нового медиа"""
        logger.debug("Создание нового медиа")

        user = await check_auth(session, api_key)

        current_file_path = Path(__file__).parent
        UPLOAD_DIR = current_file_path / "uploads"
        UPLOAD_DIR.mkdir(exist_ok=True)

        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename

        try:
            async with aiofiles.open(file_path, "wb") as out_file:
                content = await file.read()
                await out_file.write(content)

            new_media = Media(
                file_name=file.filename,
                file_path=str(file_path),
                uploaded_by=user.user_id,
            )
            session.add(new_media)
            await session.flush()

            return schema.MediaResponse(
                uploaded_by=new_media.uploaded_by,
                media_id=new_media.media_id,
            )

        except Exception:
            # Удаление медиа
            logger.error("Удаление медиа")

            if file_path.exists():
                file_path.unlink()
            raise  # Поднятие исключения для отката транзакции
