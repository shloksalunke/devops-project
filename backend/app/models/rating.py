"""Rating and RideContact models."""
from sqlalchemy import Column, String, SmallInteger, Text, DateTime, ForeignKey, UniqueConstraint, CheckConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Rating(Base):
    """Driver rating model."""
    __tablename__ = "ratings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    driver_id = Column(UUID(as_uuid=True), ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(SmallInteger, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_rating_range"),
        UniqueConstraint("driver_id", "student_id", name="uq_driver_student_rating"),
    )

    def __repr__(self):
        return f"<Rating {self.rating}* by student {self.student_id} for driver {self.driver_id}>"


class RideContact(Base):
    """Ride contact log model."""
    __tablename__ = "ride_contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False, index=True)
    contacted_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    def __repr__(self):
        return f"<RideContact student={self.student_id} driver={self.driver_id}>"
