"""
Main API router that includes all endpoint routers
"""
from fastapi import APIRouter

from app.api.v1.endpoints import health, auth, spreadsheets, websocket, files, stats


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

api_router.include_router(
    spreadsheets.router,
    tags=["Spreadsheets"],
)

api_router.include_router(
    websocket.router,
    tags=["WebSocket"],
)

api_router.include_router(
    files.router,
    tags=["Files"],
)

api_router.include_router(
    stats.router,
    tags=["Stats"],
)
