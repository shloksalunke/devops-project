"""Driver schemas."""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID


class RatingSchema(BaseModel):
    """Rating schema for embedding in driver detail."""
    id: UUID
    rating: int
    comment: str | None
    student_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class DriverListResponse(BaseModel):
    """Driver list response schema."""
    id: UUID
    name: str
    vehicle_type: str
    vehicle_details: str | None
    service_area: str | None
    is_available: bool
    avg_rating: float
    total_ratings: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "name": "Suresh Pawar",
                "vehicle_type": "auto",
                "vehicle_details": "MH-15 AG 1234, Yellow Auto",
                "service_area": "Nashik Road",
                "is_available": True,
                "avg_rating": 4.5,
                "total_ratings": 10
            }
        }


class DriverDetailResponse(BaseModel):
    """Driver detail response schema with ratings."""
    id: UUID
    name: str
    phone: str
    vehicle_type: str
    vehicle_details: str | None
    service_area: str | None
    is_available: bool
    avg_rating: float
    total_ratings: int
    ratings: list[RatingSchema] = []

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "name": "Suresh Pawar",
                "phone": "+91 98220 11111",
                "vehicle_type": "auto",
                "vehicle_details": "MH-15 AG 1234, Yellow Auto",
                "service_area": "Nashik Road",
                "is_available": True,
                "avg_rating": 4.5,
                "total_ratings": 10,
                "ratings": []
            }
        }


class DriverResponse(BaseModel):
    """Full driver response schema."""
    id: UUID
    name: str
    phone: str
    email: EmailStr
    vehicle_type: str
    vehicle_details: str | None
    service_area: str | None
    photo_url: str | None
    is_available: bool
    is_active: bool
    avg_rating: float
    total_ratings: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "name": "Suresh Pawar",
                "phone": "+91 98220 11111",
                "email": "suresh@driver.com",
                "vehicle_type": "auto",
                "vehicle_details": "MH-15 AG 1234, Yellow Auto",
                "service_area": "Nashik Road",
                "photo_url": None,
                "is_available": True,
                "is_active": True,
                "avg_rating": 4.5,
                "total_ratings": 10,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }


class CreateDriverRequest(BaseModel):
    """Create driver request schema."""
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=5, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=8)
    vehicle_type: str = Field(..., pattern="^(auto|taxi|car)$")
    vehicle_details: str | None = Field(None, max_length=200)
    service_area: str | None = Field(None, max_length=200)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Suresh Pawar",
                "phone": "+91 98220 11111",
                "email": "suresh@driver.com",
                "password": "Driver@123",
                "vehicle_type": "auto",
                "vehicle_details": "MH-15 AG 1234, Yellow Auto",
                "service_area": "Nashik Road"
            }
        }


class UpdateDriverRequest(BaseModel):
    """Update driver request schema."""
    name: str | None = Field(None, min_length=1, max_length=100)
    phone: str | None = Field(None, min_length=5, max_length=20)
    vehicle_type: str | None = Field(None, pattern="^(auto|taxi|car)$")
    vehicle_details: str | None = Field(None, max_length=200)
    service_area: str | None = Field(None, max_length=200)
    photo_url: str | None = Field(None, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Suresh Pawar",
                "phone": "+91 98220 11111",
                "vehicle_type": "auto",
                "vehicle_details": "MH-15 AG 1234, Yellow Auto",
                "service_area": "Nashik Road",
                "photo_url": None
            }
        }


class AvailabilityRequest(BaseModel):
    """Availability request schema."""
    is_available: bool

    class Config:
        json_schema_extra = {
            "example": {
                "is_available": True
            }
        }
