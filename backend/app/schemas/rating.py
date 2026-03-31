"""Rating schemas."""
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class RatingCreateRequest(BaseModel):
    """Rating creation request schema."""
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = Field(None, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "rating": 5,
                "comment": "Very punctual and polite."
            }
        }


class RatingResponse(BaseModel):
    """Rating response schema."""
    id: UUID
    driver_id: UUID
    student_id: UUID
    rating: int
    comment: str | None
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440002",
                "driver_id": "550e8400-e29b-41d4-a716-446655440001",
                "student_id": "550e8400-e29b-41d4-a716-446655440000",
                "rating": 5,
                "comment": "Very punctual and polite.",
                "created_at": "2024-01-15T10:30:00Z"
            }
        }
