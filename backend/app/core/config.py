from pydantic_settings import BaseSettings
from typing import List, Union
import os


def parse_cors_origins(value: Union[str, List[str]]) -> List[str]:
    """Парсинг CORS origins из строки (разделенные запятыми) или списка"""
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        # Разделение по запятой и очистка пробелов
        return [origin.strip() for origin in value.split(",") if origin.strip()]
    return []


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379"
    SECRET_KEY: str
    ADMIN_PASSWORD: str
    CORS_ORIGINS: str = "http://localhost:1800,http://78.107.254.30:1800,http://192.168.88.50:1800"
    
    # JWT settings
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Media settings
    MEDIA_DIR: str = "/app/media"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Получение списка CORS origins"""
        return parse_cors_origins(self.CORS_ORIGINS)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

