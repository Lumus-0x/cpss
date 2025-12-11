"""
Инициализация базы данных и создание административного пользователя
"""
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import User, UserRole
from app.core.security import get_password_hash
from app.core.config import settings


def init_db():
    """Инициализация базы данных"""
    # Создание всех таблиц
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        # Проверка существования админа
        admin = db.query(User).filter(User.username == "admin").first()
        
        if not admin:
            # Создание административного пользователя
            admin_user = User(
                username="admin",
                password_hash=get_password_hash(settings.ADMIN_PASSWORD),
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print(f"✓ Admin user created with password from ADMIN_PASSWORD env variable")
        else:
            # Обновление пароля администратора
            admin.password_hash = get_password_hash(settings.ADMIN_PASSWORD)
            db.commit()
            print(f"✓ Admin user password updated")
        
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    init_db()

