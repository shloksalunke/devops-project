"""Driver document model for RTO verification."""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class DriverDocument(Base):
    """Driver document tracking model for RTO verification."""
    __tablename__ = "driver_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    driver_id = Column(UUID(as_uuid=True), ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Document type: ID (Aadhaar/PAN), LICENSE (Driving License), RC (Vehicle Registration), INSURANCE (Optional)
    document_type = Column(String(20), nullable=False, index=True)  # ID, LICENSE, RC, INSURANCE
    
    # File information
    file_path = Column(String(500), nullable=False)  # Path to uploaded file
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    file_type = Column(String(50), nullable=False)  # pdf, jpg, png, etc.
    
    # Status tracking
    status = Column(String(20), nullable=False, default="PENDING", index=True)  # PENDING, APPROVED, REJECTED
    rejection_reason = Column(String(500), nullable=True)  # Why was it rejected
    
    # Metadata
    uploaded_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_by = Column(UUID(as_uuid=True), nullable=True)  # Admin ID who verified
    
    # Expiry tracking (for licenses and certificates)
    expiry_date = Column(DateTime(timezone=True), nullable=True)  # When document expires
    
    __table_args__ = (
        CheckConstraint("document_type IN ('ID', 'LICENSE', 'RC', 'INSURANCE')", name="ck_document_type"),
        CheckConstraint("status IN ('PENDING', 'APPROVED', 'REJECTED')", name="ck_document_status"),
    )

    def __repr__(self):
        return f"<DriverDocument {self.document_type} for driver {self.driver_id} - {self.status}>"
