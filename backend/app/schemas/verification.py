"""Verification schemas for RTO verification workflow."""
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class DriverDocumentResponse(BaseModel):
    """Driver document response schema."""
    id: UUID
    driver_id: UUID
    document_type: str  # ID, LICENSE, RC, INSURANCE
    file_name: str
    file_size: int
    file_type: str
    status: str  # PENDING, APPROVED, REJECTED
    rejection_reason: str | None
    uploaded_at: datetime
    verified_at: datetime | None
    expiry_date: datetime | None

    class Config:
        from_attributes = True


class DriverVerificationStatusResponse(BaseModel):
    """Driver verification status response."""
    driver_id: UUID
    driver_name: str
    verification_status: str  # PENDING, APPROVED, REJECTED, SUSPENDED
    verification_notes: str | None
    verified_at: datetime | None
    verified_by: UUID | None
    documents: list[DriverDocumentResponse] = []
    all_required_approved: bool

    class Config:
        from_attributes = True


class PendingDriverResponse(BaseModel):
    """Pending driver for admin approval."""
    id: UUID
    name: str
    email: str
    phone: str
    vehicle_type: str
    vehicle_details: str | None
    service_area: str | None
    verification_status: str
    created_at: datetime
    documents_uploaded: bool
    documents_count: int

    class Config:
        from_attributes = True


class ApproveDriverRequest(BaseModel):
    """Request to approve a driver."""
    notes: str | None = Field(None, max_length=1000)


class RejectDriverRequest(BaseModel):
    """Request to reject a driver."""
    reason: str = Field(..., min_length=10, max_length=1000)


class SuspendDriverRequest(BaseModel):
    """Request to suspend a driver."""
    reason: str = Field(..., min_length=10, max_length=1000)
