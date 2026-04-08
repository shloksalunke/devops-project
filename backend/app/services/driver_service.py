"""Driver service."""
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.exceptions import NotFoundError, ConflictError, BadRequestError
from app.repositories import driver_repo, rating_repo, driver_document_repo
from app.schemas.driver import CreateDriverRequest, UpdateDriverRequest
from app.services.auth_service import hash_password
from uuid import uuid4
from fastapi import UploadFile
import os
import json

# Secure filesystem-based storage for uploaded driver documents
DOC_STORE_DIR = os.path.join(os.getcwd(), 'uploads', 'drivers')
os.makedirs(DOC_STORE_DIR, exist_ok=True)

# Allowed file types and max size
ALLOWED_FILE_TYPES = {'pdf', 'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def _validate_file(upload: UploadFile) -> tuple[bool, str]:
    """Validate uploaded file."""
    if not upload:
        return True, ""
    
    # Check file type
    file_ext = os.path.splitext(upload.filename or "")[1].lstrip('.').lower()
    if file_ext not in ALLOWED_FILE_TYPES:
        return False, f"Invalid file type. Allowed: {', '.join(ALLOWED_FILE_TYPES)}"
    
    # Check file size (read size from file)
    upload.file.seek(0, os.SEEK_END)
    file_size = upload.file.tell()
    upload.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return False, f"File too large. Max size: {MAX_FILE_SIZE / (1024*1024):.1f}MB"
    
    return True, ""


def _save_uploaded_file(driver_id: str, upload: UploadFile | None, name: str) -> tuple[str | None, int | None]:
    """Save uploaded file and return path and size."""
    if not upload:
        return None, None
    
    driver_dir = os.path.join(DOC_STORE_DIR, driver_id)
    os.makedirs(driver_dir, exist_ok=True)
    filename = f"{name}_{uuid4().hex}_{os.path.basename(upload.filename)}"
    path = os.path.join(driver_dir, filename)
    
    file_size = 0
    with open(path, 'wb') as f:
        for chunk in upload.file:
            f.write(chunk)
            file_size += len(chunk)
    
    return path, file_size


def list_drivers(db: Session, vehicle_type: str | None = None) -> list:
    """List all active APPROVED drivers, optionally filtered by vehicle type.
    
    CRITICAL FIX: Only show drivers that are:
    1. is_active = True
    2. verification_status = 'APPROVED'
    """
    return driver_repo.get_all_active_approved(db, vehicle_type)


def get_driver(db: Session, driver_id: UUID) -> dict:
    """Get driver details with ratings."""
    driver = driver_repo.get_by_id(db, driver_id)
    if not driver or not driver.is_active or driver.verification_status != "APPROVED":
        raise NotFoundError("Driver not found")

    ratings = rating_repo.get_by_driver(db, driver_id)
    return {
        "id": driver.id,
        "name": driver.name,
        "phone": driver.phone,
        "vehicle_type": driver.vehicle_type,
        "vehicle_details": driver.vehicle_details,
        "service_area": driver.service_area,
        "is_available": driver.is_available,
        "avg_rating": float(driver.avg_rating),
        "total_ratings": driver.total_ratings,
        "ratings": ratings
    }


def create_driver(db: Session, data: CreateDriverRequest):
    """Create a new driver (for admin manual creation)."""
    # Check if email already exists
    existing_driver = driver_repo.get_by_email(db, data.email)
    if existing_driver:
        raise ConflictError("Email already registered")

    hashed_password = hash_password(data.password)
    driver = driver_repo.create(
        db,
        name=data.name,
        phone=data.phone,
        email=data.email,
        hashed_password=hashed_password,
        vehicle_type=data.vehicle_type,
        vehicle_details=data.vehicle_details,
        service_area=data.service_area,
        verification_status="APPROVED"  # Admin-created drivers are auto-approved
    )
    return driver


def register_driver(db: Session, name: str, phone: str, email: str, password: str, vehicle_type: str, vehicle_details: str | None = None, service_area: str | None = None, id_document: UploadFile | None = None, license_document: UploadFile | None = None, rc_document: UploadFile | None = None):
    """Register driver for admin approval with document validation.
    
    Creates driver with verification_status = 'PENDING' and stores documents in DB.
    """
    existing = driver_repo.get_by_email(db, email)
    if existing:
        raise ConflictError("Email already registered")

    # Validate files
    for upload, name_suffix in [(id_document, "ID"), (license_document, "License"), (rc_document, "RC")]:
        if upload:
            valid, msg = _validate_file(upload)
            if not valid:
                raise BadRequestError(f"{name_suffix} document: {msg}")

    hashed_password = hash_password(password)
    
    # Create driver with PENDING status
    driver = driver_repo.create(
        db,
        name=name,
        phone=phone,
        email=email,
        hashed_password=hashed_password,
        vehicle_type=vehicle_type,
        vehicle_details=vehicle_details,
        service_area=service_area,
        is_active=False,  # Inactive until approved
        is_available=False,
        verification_status="PENDING"  # CRITICAL: Drivers start as PENDING
    )

    driver_id = str(driver.id)
    
    # Save documents and track in database
    doc_types = {
        'ID': id_document,
        'LICENSE': license_document,
        'RC': rc_document
    }
    
    for doc_type, upload in doc_types.items():
        if upload:
            file_path, file_size = _save_uploaded_file(driver_id, upload, doc_type.lower())
            if file_path:
                file_ext = os.path.splitext(upload.filename or "")[1].lstrip('.').lower()
                driver_document_repo.create(
                    db,
                    driver_id=driver.id,
                    document_type=doc_type,
                    file_path=file_path,
                    file_name=upload.filename,
                    file_size=file_size or 0,
                    file_type=file_ext,
                    status="PENDING"
                )

    return driver


def update_driver(db: Session, driver_id: UUID, data: UpdateDriverRequest):
    """Update driver information."""
    driver = driver_repo.get_by_id(db, driver_id)
    if not driver:
        raise NotFoundError("Driver not found")

    update_fields = data.model_dump(exclude_unset=True)
    updated_driver = driver_repo.update(db, driver_id, **update_fields)
    return updated_driver


def deactivate_driver(db: Session, driver_id: UUID):
    """Deactivate (soft delete) a driver."""
    driver = driver_repo.get_by_id(db, driver_id)
    if not driver:
        raise NotFoundError("Driver not found")

    return driver_repo.soft_delete(db, driver_id)


def set_availability(db: Session, driver_id: UUID, is_available: bool):
    """Set driver availability."""
    driver = driver_repo.get_by_id(db, driver_id)
    if not driver:
        raise NotFoundError("Driver not found")

    return driver_repo.set_availability(db, driver_id, is_available)


# ===== VERIFICATION FUNCTIONS (NEW) =====

def get_pending_drivers(db: Session) -> list:
    """Get all drivers pending verification for admin review."""
    return driver_repo.get_pending_drivers(db)


def get_driver_verification_status(db: Session, driver_id: UUID) -> dict:
    """Get driver verification status with all documents."""
    driver = driver_repo.get_by_id(db, driver_id)
    if not driver:
        raise NotFoundError("Driver not found")
    
    documents = driver_document_repo.get_by_driver(db, driver_id)
    all_approved = driver_document_repo.all_approved(db, driver_id)
    
    # Return documents as-is (ORM objects will be serialized by Pydantic)
    return {
        "driver_id": driver.id,
        "driver_name": driver.name,
        "verification_status": driver.verification_status,
        "verification_notes": driver.verification_notes,
        "verified_at": driver.verified_at,
        "verified_by": driver.verified_by,
        "documents": documents,
        "all_required_approved": all_approved
    }


def approve_driver(db: Session, driver_id: UUID, admin_id: UUID, notes: str | None = None) -> dict:
    """Approve a driver after document verification."""
    driver = driver_repo.get_by_id(db, driver_id)
    if not driver:
        raise NotFoundError("Driver not found")
    
    # Auto-approve all pending documents since the admin has approved the driver
    docs = driver_document_repo.get_pending_for_driver(db, driver_id)
    for doc in docs:
        driver_document_repo.approve(db, doc.id, admin_id)
    
    # Update driver status
    now = datetime.now(timezone.utc)
    updated_driver = driver_repo.update(
        db,
        driver_id,
        verification_status="APPROVED",
        is_active=True,
        verified_at=now,
        verified_by=admin_id,
        verification_notes=notes
    )
    
    return {
        "message": "Driver approved successfully",
        "driver_id": str(updated_driver.id),
        "status": updated_driver.verification_status
    }


def reject_driver(db: Session, driver_id: UUID, admin_id: UUID, reason: str) -> dict:
    """Reject a driver application."""
    driver = driver_repo.get_by_id(db, driver_id)
    if not driver:
        raise NotFoundError("Driver not found")
    
    # Update driver status
    now = datetime.now(timezone.utc)
    updated_driver = driver_repo.update(
        db,
        driver_id,
        verification_status="REJECTED",
        is_active=False,
        verified_at=now,
        verified_by=admin_id,
        verification_notes=reason
    )
    
    return {
        "message": "Driver rejected",
        "driver_id": str(updated_driver.id),
        "status": updated_driver.verification_status
    }


def suspend_driver(db: Session, driver_id: UUID, admin_id: UUID, reason: str) -> dict:
    """Suspend a previously approved driver."""
    driver = driver_repo.get_by_id(db, driver_id)
    if not driver:
        raise NotFoundError("Driver not found")
    
    now = datetime.now(timezone.utc)
    updated_driver = driver_repo.update(
        db,
        driver_id,
        verification_status="SUSPENDED",
        is_active=False,
        verified_by=admin_id,
        verification_notes=reason
    )
    
    return {
        "message": "Driver suspended",
        "driver_id": str(updated_driver.id),
        "status": updated_driver.verification_status
    }


def get_admin_stats(db: Session) -> dict:
    """Get admin dashboard statistics."""
    from app.repositories.user_repo import count_students

    return {
        "total_students": count_students(db),
        "total_drivers": driver_repo.count_all(db),
        "active_drivers": driver_repo.count_active(db),
        "pending_verification": len(driver_repo.get_pending_drivers(db)),
        "total_ratings": rating_repo.count_all(db)
    }

