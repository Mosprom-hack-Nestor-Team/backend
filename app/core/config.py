"""
Application configuration module
"""
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings and configuration
    """
    # Project metadata
    PROJECT_NAME: str = "Backend API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "FastAPI backend with clean architecture"
    
    # API configuration
    API_V1_STR: str = "/api/v1"
    
    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 7878
    RELOAD: bool = True
    
    # CORS configuration
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
