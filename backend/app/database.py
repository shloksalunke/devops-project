"""Database configuration and session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Support both SQLAlchemy 2.0+ (`DeclarativeBase`) and older versions
try:
    from sqlalchemy.orm import DeclarativeBase
    DeclarativeBaseAvailable = True
except Exception:
    from sqlalchemy.ext.declarative import declarative_base
    DeclarativeBaseAvailable = False

from app.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


if DeclarativeBaseAvailable:
    class Base(DeclarativeBase):
        pass
else:
    # declarative_base() returns a base class for older SQLAlchemy versions
    Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
