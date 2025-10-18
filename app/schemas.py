"""
Pydantic schemas for request/response validation
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ============= User Schemas =============

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Token Schemas =============

class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema"""
    user_id: Optional[int] = None
    email: Optional[str] = None


class RefreshToken(BaseModel):
    """Refresh token request schema"""
    refresh_token: str


# ============= Auth Schemas =============

class AuthResponse(BaseModel):
    """Authentication response schema"""
    user: UserResponse
    token: Token
