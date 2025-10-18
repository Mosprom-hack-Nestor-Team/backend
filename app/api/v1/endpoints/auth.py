"""
Authentication endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import (
    UserCreate,
    UserLogin,
    AuthResponse,
    RefreshToken,
    Token as TokenSchema,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Register a new user
    
    - **name**: User's full name
    - **email**: User's email address
    - **password**: User's password (min 6 characters)
    """
    return AuthService.register_user(db, user_data)


@router.post("/login", response_model=AuthResponse)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Login with email and password
    
    - **email**: User's email address
    - **password**: User's password
    """
    return AuthService.login_user(db, login_data)


@router.post("/refresh", response_model=TokenSchema)
async def refresh_token(
    token_data: RefreshToken,
    db: Session = Depends(get_db),
):
    """
    Refresh access token using refresh token
    
    - **refresh_token**: Valid refresh token
    """
    return AuthService.refresh_access_token(db, token_data.refresh_token)


@router.post("/logout")
async def logout(
    token_data: RefreshToken,
    db: Session = Depends(get_db),
):
    """
    Logout user by revoking refresh token
    
    - **refresh_token**: Refresh token to revoke
    """
    return AuthService.logout_user(db, token_data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Get current authenticated user information
    
    Requires: Bearer token in Authorization header
    """
    token = credentials.credentials
    user = AuthService.get_current_user(db, token)
    return UserResponse.model_validate(user)


@router.post("/cleanup-tokens")
async def cleanup_expired_tokens(
    db: Session = Depends(get_db),
):
    """
    Admin endpoint to cleanup expired tokens
    
    This endpoint should be called periodically by a cron job
    """
    deleted_count = AuthService.cleanup_expired_tokens(db)
    return {"message": f"Deleted {deleted_count} expired tokens"}
