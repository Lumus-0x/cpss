from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import SyncChannel, Platform, SyncMessage, SyncStatus
from app.schemas import SyncChannelRequest, SyncChannelResponse
from app.core.security import get_current_user

router = APIRouter()


@router.post("/message")
async def sync_message(
    message_data: dict,
    db: Session = Depends(get_db)
):
    """Синхронизация сообщения между платформами (вызывается ботами)"""
    try:
        platform = Platform(message_data.get("platform"))
        channel_id = message_data.get("channel_id")
        platform_message_id = message_data.get("platform_message_id")
        
        # Поиск канала синхронизации
        sync_channel = db.query(SyncChannel).filter(
            SyncChannel.channel_id == channel_id,
            SyncChannel.platform == platform,
            SyncChannel.is_active == True
        ).first()
        
        if not sync_channel or not sync_channel.paired_channel_id:
            return {"status": "no_sync_config"}
        
        # Сохранение сообщения для синхронизации
        sync_message = SyncMessage(
            channel_id=sync_channel.id,
            platform=platform,
            platform_message_id=platform_message_id,
            content=message_data.get("content", ""),
            metadata=message_data.get("metadata", {}),
            status=SyncStatus.PENDING
        )
        db.add(sync_message)
        db.commit()
        
        # Здесь должна быть логика отправки в другую платформу
        # Она может быть реализована через очередь задач (Celery) или напрямую
        
        return {"status": "queued", "sync_message_id": sync_message.id}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error syncing message: {str(e)}"
        )


@router.put("/message")
async def update_sync_message(
    message_data: dict,
    db: Session = Depends(get_db)
):
    """Обновление синхронизированного сообщения"""
    try:
        platform = Platform(message_data.get("platform"))
        platform_message_id = message_data.get("platform_message_id")
        
        # Поиск существующего сообщения
        sync_message = db.query(SyncMessage).filter(
            SyncMessage.platform == platform,
            SyncMessage.platform_message_id == platform_message_id
        ).first()
        
        if sync_message:
            sync_message.content = message_data.get("content", "")
            sync_message.metadata = message_data.get("metadata", {})
            sync_message.status = SyncStatus.PENDING
            db.commit()
        
        return {"status": "updated"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating message: {str(e)}"
        )


@router.get("/channels", response_model=List[SyncChannelResponse])
async def get_sync_channels(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получение списка синхронизируемых каналов"""
    channels = db.query(SyncChannel).all()
    return channels


@router.post("/channels", response_model=SyncChannelResponse)
async def create_sync_channel(
    channel: SyncChannelRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Создание нового канала для синхронизации"""
    new_channel = SyncChannel(
        platform=channel.platform,
        channel_id=channel.channel_id,
        channel_name=channel.channel_name,
        paired_channel_id=channel.paired_channel_id,
        paired_platform=channel.paired_platform,
        config=channel.config or {}
    )
    db.add(new_channel)
    db.commit()
    db.refresh(new_channel)
    
    return new_channel


@router.put("/channels/{channel_id}", response_model=SyncChannelResponse)
async def update_sync_channel(
    channel_id: int,
    channel: SyncChannelRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Обновление канала синхронизации"""
    db_channel = db.query(SyncChannel).filter(SyncChannel.id == channel_id).first()
    if not db_channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    
    db_channel.channel_id = channel.channel_id
    db_channel.channel_name = channel.channel_name
    db_channel.paired_channel_id = channel.paired_channel_id
    db_channel.paired_platform = channel.paired_platform
    db_channel.config = channel.config or {}
    
    db.commit()
    db.refresh(db_channel)
    
    return db_channel


@router.delete("/channels/{channel_id}")
async def delete_sync_channel(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Удаление канала синхронизации"""
    channel = db.query(SyncChannel).filter(SyncChannel.id == channel_id).first()
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    
    db.delete(channel)
    db.commit()
    
    return {"message": "Channel deleted successfully"}


@router.post("/channels/{channel_id}/toggle")
async def toggle_sync_channel(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Включение/выключение синхронизации для канала"""
    channel = db.query(SyncChannel).filter(SyncChannel.id == channel_id).first()
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    
    channel.is_active = not channel.is_active
    db.commit()
    
    return {"id": channel.id, "is_active": channel.is_active}
