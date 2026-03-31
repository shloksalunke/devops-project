"""User schemas."""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID


class UserResponse(BaseModel):
    """User response schema (no password)."""
    id: UUID
    name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Aarav Mehta",
                "email": "aarav@student.edu",
                "role": "student",
                "is_active": True,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class UserUpdateRequest(BaseModel):
    """User update request schema."""
    name: str | None = Field(None, min_length=1, max_length=100)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Aarav Mehta Updated"
            }
        }


class RideContactResponse(BaseModel):
    """Ride contact response schema."""
    driver_name: str
    vehicle_type: str
    contacted_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "driver_name": "Suresh Pawar",
                "vehicle_type": "auto",
                "contacted_at": "2024-01-15T10:30:00Z"
            }
        }
