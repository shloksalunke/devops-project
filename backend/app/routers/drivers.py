"""Driver endpoints."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.driver import DriverListResponse, DriverDetailResponse, RatingSchema
from app.schemas.rating import RatingCreateRequest, RatingResponse
from app.services import driver_service, rating_service


router = APIRouter()


@router.get("", response_model=list[DriverListResponse])
async def list_drivers(
    vehicle_type: str | None = Query(None),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all active APPROVED drivers, optionally filtered by vehicle type.
    
    CRITICAL FIX: Only returns drivers with verification_status = 'APPROVED'
    This ensures students only see verified, RTO-compliant drivers.
    """
    drivers = driver_service.list_drivers(db, vehicle_type)
    return drivers


@router.get("/{driver_id}", response_model=DriverDetailResponse)
async def get_driver_detail(
    driver_id: UUID,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get driver details with ratings."""
    driver_detail = driver_service.get_driver(db, driver_id)
    return driver_detail


@router.post("/{driver_id}/contacts", status_code=status.HTTP_200_OK)
async def log_contact(
    driver_id: UUID,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log a ride contact with a driver."""
    rating_service.log_contact(db, current_user.id, driver_id)
    return {"message": "Contact logged"}


@router.post("/{driver_id}/ratings", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
async def submit_rating(
    driver_id: UUID,
    request: RatingCreateRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a rating for a driver."""
    # Only students can rate
    if current_user.role != "student":
        raise Exception("Only students can rate drivers")

    rating = rating_service.submit_rating(db, driver_id, current_user.id, request.rating, request.comment)
    return rating

