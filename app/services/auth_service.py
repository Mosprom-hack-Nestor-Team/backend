"""
Authentication service
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.config import settings
from app.models import User, Token, UserRole
from app.schemas import UserCreate, UserLogin, AuthResponse, UserResponse, Token as TokenSchema


class AuthService:
    """Authentication service"""

    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> AuthResponse:
        """
        Register a new user
        
        Args:
            db: Database session
            user_data: User registration data
            
        Returns:
            Authentication response with user and tokens
            
        Raises:
            HTTPException: If email already registered
        """
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            name=user_data.name,
            email=user_data.email,
            hashed_password=hashed_password,
            role=UserRole.USER,
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Generate tokens
        access_token = create_access_token({"sub": str(new_user.id), "email": new_user.email})
        refresh_token = create_refresh_token({"sub": str(new_user.id), "email": new_user.email})
        
        # Store refresh token in database
        token_expires = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        db_token = Token(
            user_id=new_user.id,
            token=refresh_token,
            expires_at=token_expires,
        )
        db.add(db_token)
        db.commit()
        
        # Prepare response
        user_response = UserResponse.model_validate(new_user)
        token_response = TokenSchema(access_token=access_token, refresh_token=refresh_token)
        
        return AuthResponse(user=user_response, token=token_response)

    @staticmethod
    def login_user(db: Session, login_data: UserLogin) -> AuthResponse:
        """
        Authenticate user and generate tokens
        
        Args:
            db: Database session
            login_data: User login credentials
            
        Returns:
            Authentication response with user and tokens
            
        Raises:
            HTTPException: If credentials are invalid
        """
        # Find user by email
        user = db.query(User).filter(User.email == login_data.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        
        # Verify password
        if not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        
        # Generate tokens
        access_token = create_access_token({"sub": str(user.id), "email": user.email})
        refresh_token = create_refresh_token({"sub": str(user.id), "email": user.email})
        
        # Store refresh token in database
        token_expires = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        db_token = Token(
            user_id=user.id,
            token=refresh_token,
            expires_at=token_expires,
        )
        db.add(db_token)
        db.commit()
        
        # Prepare response
        user_response = UserResponse.model_validate(user)
        token_response = TokenSchema(access_token=access_token, refresh_token=refresh_token)
        
        return AuthResponse(user=user_response, token=token_response)

    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> TokenSchema:
        """
        Refresh access token using refresh token
        
        Args:
            db: Database session
            refresh_token: Refresh token
            
        Returns:
            New token pair
            
        Raises:
            HTTPException: If refresh token is invalid or expired
        """
        # Decode refresh token
        payload = decode_token(refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        
        # Check if token exists in database and not expired
        db_token = db.query(Token).filter(
            Token.token == refresh_token,
            Token.expires_at > datetime.utcnow()
        ).first()
        
        if not db_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired or invalid",
            )
        
        # Get user
        user = db.query(User).filter(User.id == db_token.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        
        # Generate new tokens
        new_access_token = create_access_token({"sub": str(user.id), "email": user.email})
        new_refresh_token = create_refresh_token({"sub": str(user.id), "email": user.email})
        
        # Update refresh token in database
        db_token.token = new_refresh_token
        db_token.expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        db.commit()
        
        return TokenSchema(access_token=new_access_token, refresh_token=new_refresh_token)

    @staticmethod
    def logout_user(db: Session, refresh_token: str) -> dict:
        """
        Logout user by removing refresh token
        
        Args:
            db: Database session
            refresh_token: Refresh token to revoke
            
        Returns:
            Success message
        """
        # Delete token from database
        db.query(Token).filter(Token.token == refresh_token).delete()
        db.commit()
        
        return {"message": "Successfully logged out"}

    @staticmethod
    def get_current_user(db: Session, token: str) -> User:
        """
        Get current user from access token
        
        Args:
            db: Database session
            token: Access token
            
        Returns:
            User object
            
        Raises:
            HTTPException: If token is invalid or user not found
        """
        # Decode token
        payload = decode_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user

    @staticmethod
    def cleanup_expired_tokens(db: Session) -> int:
        """
        Remove expired tokens from database
        
        Args:
            db: Database session
            
        Returns:
            Number of tokens deleted
        """
        deleted = db.query(Token).filter(Token.expires_at < datetime.utcnow()).delete()
        db.commit()
        return deleted
