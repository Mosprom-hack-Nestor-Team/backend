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
from app.core.mongodb import MongoDB
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
    
    # Initialize PostgreSQL database - create tables if they don't exist
    try:
        print("📊 Initializing PostgreSQL database...")
        Base.metadata.create_all(bind=engine)
        print("✅ PostgreSQL database initialized successfully")
    except Exception as e:
        print(f"❌ PostgreSQL database initialization failed: {e}")
    
    # Initialize MongoDB connection
    try:
        print("📊 Connecting to MongoDB...")
        await MongoDB.connect_db()
        print("✅ MongoDB connected successfully")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
    
    # Start background task for token cleanup
    cleanup_task = asyncio.create_task(cleanup_expired_tokens_task())
    print("🧹 Started background token cleanup task")
    
    yield
    
    # Shutdown
    cleanup_task.cancel()
    
    # Close MongoDB connection
    try:
        await MongoDB.close_db()
    except Exception as e:
        print(f"❌ MongoDB disconnect error: {e}")
    
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

    # Configure CORS to avoid issues in different environments
    # If specific origins are provided, allow credentials with that whitelist.
    # Otherwise, allow all origins without credentials to fully avoid CORS blocks.
    allowed_origins = [o.strip() for o in (settings.ALLOWED_ORIGINS or []) if o and o.strip()]
    allow_all = (not allowed_origins) or ("*" in allowed_origins)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if allow_all else allowed_origins,
        allow_credentials=False if allow_all else True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Include API router
    application.include_router(api_router, prefix=settings.API_V1_STR)

    return application


app = create_application()
