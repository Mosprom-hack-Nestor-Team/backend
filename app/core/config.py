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
    RELOAD: bool = False
    
    # CORS configuration - can be overridden via environment variable
    # Format: JSON array like ["*"] or ["https://domain.com"]
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Database configuration
    POSTGRES_USER: str = "appuser"
    POSTGRES_PASSWORD: str = "apppassword"
    POSTGRES_DB: str = "appdb"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = "postgresql://appuser:apppassword@localhost:5432/appdb"
    
    # MongoDB configuration
    MONGO_INITDB_ROOT_USERNAME: str = "admin"
    MONGO_INITDB_ROOT_PASSWORD: str = "admin123"
    MONGO_INITDB_DATABASE: str = "spreadsheets"
    MONGODB_HOST: str = "localhost"
    MONGODB_PORT: int = 27017
    MONGODB_URL: str = "mongodb://admin:admin123@localhost:27017"
    MONGODB_DB_NAME: str = "spreadsheets"
    
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
