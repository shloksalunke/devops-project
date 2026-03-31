"""Rating repository."""
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.rating import Rating, RideContact


def get_by_driver_and_student(db: Session, driver_id: UUID, student_id: UUID) -> Rating | None:
    """Get rating by driver and student."""
    return db.query(Rating).filter(
        Rating.driver_id == driver_id,
        Rating.student_id == student_id
    ).first()


def create(db: Session, driver_id: UUID, student_id: UUID, rating: int, comment: str | None = None) -> Rating:
    """Create a new rating."""
    new_rating = Rating(driver_id=driver_id, student_id=student_id, rating=rating, comment=comment)
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    return new_rating


def get_by_driver(db: Session, driver_id: UUID, limit: int = 10) -> list[Rating]:
    """Get ratings for a driver."""
    return db.query(Rating).filter(Rating.driver_id == driver_id).order_by(Rating.created_at.desc()).limit(limit).all()


def count_all(db: Session) -> int:
    """Count all ratings."""
    return db.query(Rating).count()


def log_contact(db: Session, student_id: UUID, driver_id: UUID) -> RideContact:
    """Log a ride contact."""
    contact = RideContact(student_id=student_id, driver_id=driver_id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def get_contacts_by_student(db: Session, student_id: UUID) -> list:
    """Get ride contacts for a student with driver info."""
    contacts = db.query(RideContact).filter(RideContact.student_id == student_id).all()
    result = []
    for contact in contacts:
        from app.repositories.driver_repo import get_by_id as get_driver_by_id
        driver = get_driver_by_id(db, contact.driver_id)
        if driver:
            result.append({
                "driver_name": driver.name,
                "vehicle_type": driver.vehicle_type,
                "contacted_at": contact.contacted_at
            })
    return result
