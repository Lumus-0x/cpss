from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import os
import uuid
import aiofiles
from app.database import get_db
from app.models import PublicationQueue, MediaContent, Preset, PublicationStatus
from app.schemas import PublishRequest, PublicationQueueResponse
from app.core.security import get_current_user
from app.core.config import settings

router = APIRouter()


@router.post("/upload")
async def upload_media(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Загрузка медиафайла"""
    # Проверка размера файла
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds maximum allowed size"
        )
    
    # Генерация уникального имени файла
    file_ext = os.path.splitext(file.filename or "")[1]
    if not file_ext and file.content_type:
        # Попытка определить расширение по MIME типу
        mime_extensions = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "video/mp4": ".mp4",
            "application/pdf": ".pdf"
        }
        file_ext = mime_extensions.get(file.content_type, "")
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(settings.MEDIA_DIR, unique_filename)
    
    # Сохранение файла
    os.makedirs(settings.MEDIA_DIR, exist_ok=True)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)
    
    # Сохранение информации в БД
    media = MediaContent(
        filename=unique_filename,
        original_filename=file.filename,
        file_path=file_path,
        file_type=file_ext[1:] if file_ext else "unknown",
        file_size=file_size,
        mime_type=file.content_type
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    
    return {
        "id": media.id,
        "filename": media.filename,
        "original_filename": media.original_filename,
        "file_size": media.file_size,
        "mime_type": media.mime_type
    }


@router.post("", response_model=PublicationQueueResponse)
async def create_publication(
    request: PublishRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Создание публикации"""
    # Проверка существования пресета
    preset = db.query(Preset).filter(Preset.id == request.preset_id).first()
    if not preset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preset not found"
        )
    
    # Проверка существования медиа
    if request.media_id:
        media = db.query(MediaContent).filter(MediaContent.id == request.media_id).first()
        if not media:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Media not found"
            )
    
    # Создание публикации
    publication = PublicationQueue(
        preset_id=request.preset_id,
        media_id=request.media_id,
        title=request.title,
        description=request.description,
        scheduled_at=request.scheduled_at,
        status=PublicationStatus.QUEUED if not request.scheduled_at else PublicationStatus.DRAFT
    )
    db.add(publication)
    db.commit()
    db.refresh(publication)
    
    return publication

