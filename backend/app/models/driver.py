"""Driver model."""
from sqlalchemy import Column, String, Boolean, DateTime, Numeric, Integer, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Driver(Base):
    """Driver model."""
    __tablename__ = "drivers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    vehicle_type = Column(String(20), nullable=False, index=True)
    vehicle_details = Column(String(200), nullable=True)
    service_area = Column(String(200), nullable=True)
    photo_url = Column(String(500), nullable=True)
    is_available = Column(Boolean, default=True, index=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # RTO Verification Fields (CRITICAL for safety)
    verification_status = Column(String(20), nullable=False, default="PENDING", index=True)  # PENDING, APPROVED, REJECTED, SUSPENDED
    verification_notes = Column(String(1000), nullable=True)  # Rejection/suspension reason
    verified_at = Column(DateTime(timezone=True), nullable=True)  # When was it verified
    verified_by = Column(UUID(as_uuid=True), nullable=True)  # Which admin verified it
    
    avg_rating = Column(Numeric(3, 2), default=0.0)
    total_ratings = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Driver {self.name} ({self.email}) - {self.verification_status}>"
