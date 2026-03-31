"""Rating service."""
from uuid import UUID
from sqlalchemy.orm import Session

from app.exceptions import NotFoundError, ConflictError
from app.repositories import rating_repo, driver_repo
from app.models.rating import Rating


def submit_rating(db: Session, driver_id: UUID, student_id: UUID, rating: int, comment: str | None = None) -> Rating:
    """Submit a rating for a driver."""
    # Verify driver exists and is active
    driver = driver_repo.get_by_id(db, driver_id)
    if not driver or not driver.is_active:
        raise NotFoundError("Driver not found")

    # Check for duplicate rating
    existing_rating = rating_repo.get_by_driver_and_student(db, driver_id, student_id)
    if existing_rating:
        raise ConflictError("You have already rated this driver")

    # Create rating
    new_rating = rating_repo.create(db, driver_id, student_id, rating, comment)

    # Update driver rating stats
    driver_repo.update_rating_stats(db, driver_id)

    return new_rating


def get_driver_ratings(db: Session, driver_id: UUID, limit: int = 10) -> list[Rating]:
    """Get ratings for a driver."""
    driver = driver_repo.get_by_id(db, driver_id)
    if not driver:
        raise NotFoundError("Driver not found")

    return rating_repo.get_by_driver(db, driver_id, limit)


def log_contact(db: Session, student_id: UUID, driver_id: UUID):
    """Log a ride contact."""
    driver = driver_repo.get_by_id(db, driver_id)
    if not driver:
        raise NotFoundError("Driver not found")

    return rating_repo.log_contact(db, student_id, driver_id)


def get_student_contacts(db: Session, student_id: UUID) -> list:
    """Get ride contacts for a student."""
    return rating_repo.get_contacts_by_student(db, student_id)
