from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import PublicationQueue, PublicationStatus
from app.schemas import PublicationQueueResponse
from app.core.security import get_current_user

router = APIRouter()


@router.get("", response_model=List[PublicationQueueResponse])
async def get_queue(
    status_filter: Optional[PublicationStatus] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получение очереди публикаций"""
    query = db.query(PublicationQueue)
    
    if status_filter:
        query = query.filter(PublicationQueue.status == status_filter)
    
    publications = query.order_by(PublicationQueue.created_at.desc()).limit(limit).all()
    return publications


@router.get("/{publication_id}", response_model=PublicationQueueResponse)
async def get_publication(
    publication_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получение информации о публикации"""
    publication = db.query(PublicationQueue).filter(PublicationQueue.id == publication_id).first()
    if not publication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publication not found"
        )
    return publication


@router.delete("/{publication_id}")
async def delete_publication(
    publication_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Удаление публикации из очереди"""
    publication = db.query(PublicationQueue).filter(PublicationQueue.id == publication_id).first()
    if not publication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publication not found"
        )
    
    db.delete(publication)
    db.commit()
    
    return {"message": "Publication deleted successfully"}

