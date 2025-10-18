"""
Main API router that includes all endpoint routers
"""
from fastapi import APIRouter

from app.api.v1.endpoints import health, auth


api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    health.router,
    tags=["Health"],
)

api_router.include_router(
    auth.router,
    tags=["Authentication"],
)
