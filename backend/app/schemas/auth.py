"""Authentication schemas."""
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """User registration request schema."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Aarav Mehta",
                "email": "aarav@student.edu",
                "password": "Student@123"
            }
        }


class LoginRequest(BaseModel):
    """User login request schema."""
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "aarav@student.edu",
                "password": "Student@123"
            }
        }


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGc...",
                "refresh_token": "eyJhbGc...",
                "token_type": "bearer"
            }
        }


class RefreshRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGc..."
            }
        }
