from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


class Platform(str, enum.Enum):
    TELEGRAM = "telegram"
    DISCORD = "discord"
    YOUTUBE = "youtube"
    RUTUBE = "rutube"
    TWITCH = "twitch"


class SyncStatus(str, enum.Enum):
    PENDING = "pending"
    SYNCING = "syncing"
    COMPLETED = "completed"
    FAILED = "failed"


class PublicationStatus(str, enum.Enum):
    DRAFT = "draft"
    QUEUED = "queued"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)


class BotConfig(Base):
    __tablename__ = "bots_config"
    
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(Enum(Platform), nullable=False, unique=True)
    token = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    config = Column(JSON, default={})
    last_health_check = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SyncChannel(Base):
    __tablename__ = "sync_channels"
    
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(Enum(Platform), nullable=False)
    channel_id = Column(String, nullable=False)
    channel_name = Column(String, nullable=True)
    paired_channel_id = Column(String, nullable=True)  # ID связанного канала
    paired_platform = Column(Enum(Platform), nullable=True)
    is_active = Column(Boolean, default=True)
    config = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    sync_messages = relationship("SyncMessage", back_populates="channel")


class SyncMessage(Base):
    __tablename__ = "sync_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("sync_channels.id"), nullable=False)
    platform = Column(Enum(Platform), nullable=False)
    platform_message_id = Column(String, nullable=False)
    paired_message_id = Column(String, nullable=True)  # ID сообщения в связанной платформе
    paired_platform = Column(Enum(Platform), nullable=True)
    content = Column(Text, nullable=True)
    metadata = Column(JSON, default={})
    status = Column(Enum(SyncStatus), default=SyncStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    channel = relationship("SyncChannel", back_populates="sync_messages")


class Preset(Base):
    __tablename__ = "presets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    platform = Column(Enum(Platform), nullable=False)
    config = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MediaContent(Base):
    __tablename__ = "media_content"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=True)
    metadata = Column(JSON, default={})
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PublicationQueue(Base):
    __tablename__ = "publication_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    preset_id = Column(Integer, ForeignKey("presets.id"), nullable=False)
    media_id = Column(Integer, ForeignKey("media_content.id"), nullable=True)
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(PublicationStatus), default=PublicationStatus.DRAFT)
    result = Column(JSON, default={})
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    preset = relationship("Preset")
    media = relationship("MediaContent")


class AuditLog(Base):
    __tablename__ = "audit_log"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=True)
    resource_id = Column(Integer, nullable=True)
    details = Column(JSON, default={})
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

