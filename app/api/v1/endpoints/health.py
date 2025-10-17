"""
Health check endpoint
"""
from datetime import datetime
from typing import Dict

from fastapi import APIRouter, status
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """
    Health check response model
    """
    status: str
    message: str
    timestamp: str
    version: str


router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check if the API is running and healthy",
    response_description="API health status",
)
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint to verify API is running
    
    Returns:
        Dict[str, str]: Health status information
    """
    return {
        "status": "healthy",
        "message": "API is running successfully",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
    }
