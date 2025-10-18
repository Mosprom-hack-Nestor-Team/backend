"""
Main application module for FastAPI backend
"""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.services.auth_service import AuthService


# Background task for cleaning expired tokens
async def cleanup_expired_tokens_task():
    """Background task to clean expired tokens every hour"""
    while True:
        try:
            await asyncio.sleep(3600)  # Run every hour
            db = SessionLocal()
            try:
                deleted = AuthService.cleanup_expired_tokens(db)
                print(f"🧹 Cleaned up {deleted} expired tokens")
            finally:
                db.close()
        except Exception as e:
            print(f"❌ Token cleanup error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    print(f"🚀 {settings.PROJECT_NAME} v{settings.VERSION} starting up...")
    
    # Initialize database - create tables if they don't exist
    try:
        print("📊 Initializing database...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
    
    # Start background task for token cleanup
    cleanup_task = asyncio.create_task(cleanup_expired_tokens_task())
    print("🧹 Started background token cleanup task")
    
    yield
    
    # Shutdown
    cleanup_task.cancel()
    print(f"🛑 {settings.PROJECT_NAME} shutting down...")


def create_application() -> FastAPI:
    """
    Create and configure FastAPI application instance
    
    Returns:
        FastAPI: Configured application instance
    """
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
        lifespan=lifespan,
    )

    # Set up CORS middleware - allow all origins for deployment flexibility
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API router
    application.include_router(api_router, prefix=settings.API_V1_STR)

    return application


app = create_application()
