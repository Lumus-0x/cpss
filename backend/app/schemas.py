from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models import Platform, SyncStatus, PublicationStatus, UserRole


# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    username: str
    password: str


# Bot schemas
class BotStatus(BaseModel):
    platform: Platform
    is_active: bool
    last_health_check: Optional[datetime]
    status: str  # online, offline, error


class BotConfigRequest(BaseModel):
    platform: Platform
    token: str
    config: Optional[Dict[str, Any]] = {}


class BotConfigResponse(BaseModel):
    id: int
    platform: Platform
    is_active: bool
    config: Dict[str, Any]
    last_health_check: Optional[datetime]
    
    class Config:
        from_attributes = True


# Sync channel schemas
class SyncChannelRequest(BaseModel):
    platform: Platform
    channel_id: str
    channel_name: Optional[str] = None
    paired_channel_id: Optional[str] = None
    paired_platform: Optional[Platform] = None
    config: Optional[Dict[str, Any]] = {}


class SyncChannelResponse(BaseModel):
    id: int
    platform: Platform
    channel_id: str
    channel_name: Optional[str]
    paired_channel_id: Optional[str]
    paired_platform: Optional[Platform]
    is_active: bool
    config: Dict[str, Any]
    
    class Config:
        from_attributes = True


# Preset schemas
class PresetRequest(BaseModel):
    name: str
    platform: Platform
    config: Dict[str, Any]


class PresetResponse(BaseModel):
    id: int
    name: str
    platform: Platform
    config: Dict[str, Any]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Publication schemas
class PublishRequest(BaseModel):
    preset_id: int
    media_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class PublicationQueueResponse(BaseModel):
    id: int
    preset_id: int
    media_id: Optional[int]
    title: Optional[str]
    description: Optional[str]
    scheduled_at: Optional[datetime]
    status: PublicationStatus
    result: Dict[str, Any]
    created_at: datetime
    published_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Dashboard schemas
class DashboardStats(BaseModel):
    bots_status: List[BotStatus]
    total_syncs: int
    successful_syncs: int
    failed_syncs: int
    queue_size: int
    recent_activities: List[Dict[str, Any]]

