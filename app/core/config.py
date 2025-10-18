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
    
    # Database configuration
    POSTGRES_USER: str = "appuser"
    POSTGRES_PASSWORD: str = "apppassword"
    POSTGRES_DB: str = "appdb"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = "postgresql://appuser:apppassword@localhost:5432/appdb"
    
    # JWT configuration
    JWT_SECRET_KEY: str = "your-secret-key-change-this-in-production-min-32-chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Password hashing
    PASSWORD_HASH_SCHEMES: str = "bcrypt"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
