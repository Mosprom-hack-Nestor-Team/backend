"""
Main application module for FastAPI backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings


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


@app.on_event("startup")
async def startup_event():
    """
    Actions to perform on application startup
    """
    print(f"🚀 {settings.PROJECT_NAME} v{settings.VERSION} starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Actions to perform on application shutdown
    """
    print(f"🛑 {settings.PROJECT_NAME} shutting down...")
