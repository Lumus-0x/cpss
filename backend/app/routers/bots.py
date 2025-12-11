from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import BotConfig, Platform
from app.schemas import BotStatus, BotConfigRequest, BotConfigResponse
from app.core.security import get_current_user
import httpx

router = APIRouter()


@router.post("/health")
async def update_bot_health(
    data: dict,
    db: Session = Depends(get_db)
):
    """Обновление статуса здоровья бота (вызывается ботами)"""
    platform = Platform(data.get("platform"))
    bot = db.query(BotConfig).filter(BotConfig.platform == platform).first()
    if bot:
        bot.last_health_check = datetime.utcnow()
        db.commit()
    return {"status": "ok"}


@router.get("/status", response_model=List[BotStatus])
async def get_bots_status(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получение статуса всех ботов"""
    bots = db.query(BotConfig).all()
    statuses = []
    
    for bot in bots:
        status_text = "offline"
        if bot.last_health_check:
            time_diff = (datetime.utcnow() - bot.last_health_check).total_seconds()
            if time_diff < 300:  # 5 минут
                status_text = "online"
            else:
                status_text = "error"
        
        statuses.append(BotStatus(
            platform=bot.platform,
            is_active=bot.is_active,
            last_health_check=bot.last_health_check,
            status=status_text
        ))
    
    return statuses


@router.post("/configure", response_model=BotConfigResponse)
async def configure_bot(
    config: BotConfigRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Настройка бота"""
    bot = db.query(BotConfig).filter(BotConfig.platform == config.platform).first()
    
    if bot:
        bot.token = config.token
        bot.config = config.config
        bot.updated_at = datetime.utcnow()
    else:
        bot = BotConfig(
            platform=config.platform,
            token=config.token,
            config=config.config
        )
        db.add(bot)
    
    db.commit()
    db.refresh(bot)
    
    return bot


@router.get("/configure/{platform}", response_model=BotConfigResponse)
async def get_bot_config(
    platform: Platform,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получение конфигурации бота"""
    bot = db.query(BotConfig).filter(BotConfig.platform == platform).first()
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot configuration for {platform} not found"
        )
    return bot


@router.post("/configure/{platform}/toggle")
async def toggle_bot(
    platform: Platform,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Включение/выключение бота"""
    bot = db.query(BotConfig).filter(BotConfig.platform == platform).first()
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot configuration for {platform} not found"
        )
    
    bot.is_active = not bot.is_active
    db.commit()
    
    return {"platform": platform, "is_active": bot.is_active}
