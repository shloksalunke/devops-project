"""User endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.schemas.user import UserResponse, UserUpdateRequest, RideContactResponse
from app.repositories import user_repo
from app.services import rating_service


router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(require_role("student", "admin")), db: Session = Depends(get_db)):
    """Get current authenticated user."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    request: UserUpdateRequest,
    current_user = Depends(require_role("student", "admin")),
    db: Session = Depends(get_db)
):
    """Update current user information."""
    updated_user = user_repo.update(db, current_user.id, **request.model_dump(exclude_unset=True))
    return updated_user


@router.get("/me/contacts", response_model=list[RideContactResponse])
async def get_my_contacts(current_user = Depends(require_role("student", "admin")), db: Session = Depends(get_db)):
    """Get ride contacts for current user."""
    contacts = rating_service.get_student_contacts(db, current_user.id)
    return contacts
