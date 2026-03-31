"""Driver repository."""
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, text

from app.models.driver import Driver


def get_by_id(db: Session, driver_id: UUID) -> Driver | None:
    """Get driver by ID."""
    return db.query(Driver).filter(Driver.id == driver_id).first()


def get_by_email(db: Session, email: str) -> Driver | None:
    """Get driver by email."""
    return db.query(Driver).filter(Driver.email == email).first()


def get_all_active(db: Session, vehicle_type: str | None = None) -> list[Driver]:
    """Get all active drivers (deprecated - use get_all_active_approved instead)."""
    query = db.query(Driver).filter(Driver.is_active == True)
    if vehicle_type:
        query = query.filter(Driver.vehicle_type == vehicle_type)
    return query.all()


def get_all_active_approved(db: Session, vehicle_type: str | None = None) -> list[Driver]:
    """Get all active AND APPROVED drivers - CRITICAL FIX for safety.
    
    Only drivers that are:
    1. is_active = True
    2. verification_status = 'APPROVED'
    
    This ensures only verified drivers appear in search results.
    """
    query = db.query(Driver).filter(
        Driver.is_active == True,
        Driver.verification_status == "APPROVED"
    )
    if vehicle_type:
        query = query.filter(Driver.vehicle_type == vehicle_type)
    return query.all()


def get_pending_drivers(db: Session) -> list[Driver]:
    """Get all drivers pending verification for admin review."""
    return db.query(Driver).filter(
        Driver.verification_status == "PENDING"
    ).order_by(Driver.created_at.desc()).all()


def get_paginated(db: Session, skip: int = 0, limit: int = 20) -> list[Driver]:
    """Get drivers with pagination."""
    return db.query(Driver).offset(skip).limit(limit).all()


def create(db: Session, **fields) -> Driver:
    """Create a new driver."""
    driver = Driver(**fields)
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


def update(db: Session, driver_id: UUID, **fields) -> Driver:
    """Update driver fields."""
    driver = get_by_id(db, driver_id)
    if driver:
        for key, value in fields.items():
            if value is not None and hasattr(driver, key):
                setattr(driver, key, value)
        db.commit()
        db.refresh(driver)
    return driver


def soft_delete(db: Session, driver_id: UUID) -> Driver:
    """Soft delete driver (set is_active=False)."""
    return update(db, driver_id, is_active=False)


def set_availability(db: Session, driver_id: UUID, is_available: bool) -> Driver:
    """Set driver availability."""
    return update(db, driver_id, is_available=is_available)


def update_rating_stats(db: Session, driver_id: UUID) -> None:
    """Update driver rating statistics atomically."""
    db.execute(
        text("""
        UPDATE drivers
        SET avg_rating = COALESCE((SELECT ROUND(AVG(rating)::numeric, 2) FROM ratings WHERE driver_id = :driver_id), 0.0),
            total_ratings = COALESCE((SELECT COUNT(*) FROM ratings WHERE driver_id = :driver_id), 0)
        WHERE id = :driver_id
        """),
        {"driver_id": driver_id}
    )
    db.commit()


def count_active(db: Session) -> int:
    """Count active drivers (ANY status - use with caution)."""
    return db.query(Driver).filter(Driver.is_active == True).count()


def count_approved(db: Session) -> int:
    """Count approved drivers."""
    return db.query(Driver).filter(Driver.verification_status == "APPROVED").count()


def count_all(db: Session) -> int:
    """Count all drivers."""
    return db.query(Driver).count()
