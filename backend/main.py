from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from app.database import engine, Base
from app.routers import auth, bots, presets, publish, queue, sync
from app.core.config import settings
from app.middleware.ip_middleware import IPMiddleware


def init_admin_user():
    """Инициализация административного пользователя"""
    from app.database import SessionLocal
    from app.models import User, UserRole
    from app.core.security import get_password_hash
    from app.core.config import settings
    
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin_user = User(
                username="admin",
                password_hash=get_password_hash(settings.ADMIN_PASSWORD),
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("✓ Admin user created")
        else:
            admin.password_hash = get_password_hash(settings.ADMIN_PASSWORD)
            db.commit()
            print("✓ Admin user password updated")
    except Exception as e:
        print(f"Warning: Could not initialize admin user: {e}")
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    init_admin_user()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="CPSS API",
    description="Cross-Platform Sync System API",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(IPMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(bots.router, prefix="/api/bots", tags=["bots"])
app.include_router(presets.router, prefix="/api/presets", tags=["presets"])
app.include_router(publish.router, prefix="/api/publish", tags=["publish"])
app.include_router(queue.router, prefix="/api/queue", tags=["queue"])
app.include_router(sync.router, prefix="/api/sync", tags=["sync"])


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"message": "CPSS API", "version": "1.0.0"}

