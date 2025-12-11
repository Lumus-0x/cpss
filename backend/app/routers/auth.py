from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta
import redis
from app.database import get_db
from app.models import User, AuditLog
from app.schemas import Token, LoginRequest
from app.core.security import verify_password, create_access_token, get_password_hash
from app.core.config import settings

router = APIRouter()
security = HTTPBearer()
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def check_brute_force(ip_address: str) -> bool:
    """Проверка защиты от brute-force атак"""
    key = f"login_attempts:{ip_address}"
    attempts = redis_client.get(key)
    if attempts and int(attempts) >= 5:
        return True
    return False


def increment_attempts(ip_address: str):
    """Увеличение счетчика попыток"""
    key = f"login_attempts:{ip_address}"
    redis_client.incr(key)
    redis_client.expire(key, 300)  # 5 минут


def reset_attempts(ip_address: str):
    """Сброс счетчика попыток"""
    key = f"login_attempts:{ip_address}"
    redis_client.delete(key)


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Аутентификация пользователя"""
    client_ip = getattr(request.state, "client_ip", "unknown")
    
    # Проверка brute-force
    if check_brute_force(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    # Поиск пользователя
    user = db.query(User).filter(User.username == login_data.username).first()
    
    # Проверка пароля (для админа - проверка через переменную окружения)
    if login_data.username == "admin":
        if not verify_password(login_data.password, get_password_hash(settings.ADMIN_PASSWORD)):
            increment_attempts(client_ip)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
    elif not user or not verify_password(login_data.password, user.password_hash):
        increment_attempts(client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Сброс счетчика при успешном входе
    reset_attempts(client_ip)
    
    # Создание токена
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": login_data.username}, expires_delta=access_token_expires
    )
    
    # Обновление времени последнего входа
    if user:
        from datetime import datetime
        user.last_login = datetime.utcnow()
        db.commit()
    
    # Логирование
    audit_log = AuditLog(
        user_id=user.id if user else None,
        action="login",
        resource_type="user",
        ip_address=client_ip
    )
    db.add(audit_log)
    db.commit()
    
    return {"access_token": access_token, "token_type": "bearer"}

