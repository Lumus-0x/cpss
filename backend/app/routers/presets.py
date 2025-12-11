from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Preset
from app.schemas import PresetRequest, PresetResponse
from app.core.security import get_current_user

router = APIRouter()


@router.get("", response_model=List[PresetResponse])
async def get_presets(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получение списка всех пресетов"""
    presets = db.query(Preset).all()
    return presets


@router.post("", response_model=PresetResponse)
async def create_preset(
    preset: PresetRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Создание нового пресета"""
    # Проверка на дубликат имени
    existing = db.query(Preset).filter(Preset.name == preset.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Preset with this name already exists"
        )
    
    new_preset = Preset(
        name=preset.name,
        platform=preset.platform,
        config=preset.config
    )
    db.add(new_preset)
    db.commit()
    db.refresh(new_preset)
    
    return new_preset


@router.put("/{preset_id}", response_model=PresetResponse)
async def update_preset(
    preset_id: int,
    preset: PresetRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Обновление пресета"""
    db_preset = db.query(Preset).filter(Preset.id == preset_id).first()
    if not db_preset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preset not found"
        )
    
    db_preset.name = preset.name
    db_preset.platform = preset.platform
    db_preset.config = preset.config
    db.commit()
    db.refresh(db_preset)
    
    return db_preset


@router.delete("/{preset_id}")
async def delete_preset(
    preset_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Удаление пресета"""
    preset = db.query(Preset).filter(Preset.id == preset_id).first()
    if not preset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preset not found"
        )
    
    db.delete(preset)
    db.commit()
    
    return {"message": "Preset deleted successfully"}

