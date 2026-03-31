"""Driver portal endpoints."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_role
from app.schemas.driver import DriverResponse, UpdateDriverRequest, AvailabilityRequest
from app.schemas.rating import RatingResponse
from app.services import driver_service, rating_service
from app.repositories import driver_repo


router = APIRouter()


@router.get("/me", response_model=DriverResponse)
async def get_driver_profile(
    current_user = Depends(require_role("driver")),
    db: Session = Depends(get_db)
):
    """Get current driver profile."""
    return current_user


@router.put("/me", response_model=DriverResponse)
async def update_driver_profile(
    request: UpdateDriverRequest,
    current_user = Depends(require_role("driver")),
    db: Session = Depends(get_db)
):
    """Update driver profile."""
    driver = driver_service.update_driver(db, current_user.id, request)
    return driver


@router.put("/me/availability", status_code=status.HTTP_200_OK)
async def set_driver_availability(
    request: AvailabilityRequest,
    current_user = Depends(require_role("driver")),
    db: Session = Depends(get_db)
):
    """Set driver availability."""
    driver_service.set_availability(db, current_user.id, request.is_available)
    return {"is_available": request.is_available}


@router.get("/me/ratings", response_model=list[RatingResponse])
async def get_driver_ratings(
    current_user = Depends(require_role("driver")),
    db: Session = Depends(get_db)
):
    """Get ratings for current driver."""
    ratings = rating_service.get_driver_ratings(db, current_user.id)
    return ratings
