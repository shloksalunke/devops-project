"""User repository."""
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User


def get_by_id(db: Session, user_id: UUID) -> User | None:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_by_email(db: Session, email: str) -> User | None:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def create(db: Session, name: str, email: str, hashed_password: str, role: str = "student") -> User:
    """Create a new user."""
    user = User(name=name, email=email, hashed_password=hashed_password, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update(db: Session, user_id: UUID, **fields) -> User:
    """Update user fields."""
    user = get_by_id(db, user_id)
    if user:
        for key, value in fields.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)
        db.commit()
        db.refresh(user)
    return user


def get_all(db: Session, skip: int = 0, limit: int = 20) -> list[User]:
    """Get all users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()


def count_students(db: Session) -> int:
    """Count active students."""
    return db.query(User).filter(User.role == "student", User.is_active == True).count()
