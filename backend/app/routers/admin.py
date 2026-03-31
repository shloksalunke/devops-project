"""Admin endpoints."""
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from uuid import UUID
import os

from app.database import get_db
from app.dependencies import require_role
from app.schemas.driver import DriverResponse, CreateDriverRequest, UpdateDriverRequest
from app.schemas.user import UserResponse
from app.schemas.verification import (
    PendingDriverResponse, ApproveDriverRequest, RejectDriverRequest, 
    DriverVerificationStatusResponse, SuspendDriverRequest
)
from app.services import driver_service
from app.repositories import user_repo, driver_repo, driver_document_repo
from app.exceptions import NotFoundError, BadRequestError


router = APIRouter()


@router.get("/stats")
async def get_admin_stats(
    current_user = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Get admin dashboard statistics."""
    return driver_service.get_admin_stats(db)


# ===== DRIVER VERIFICATION ENDPOINTS (NEW) =====

@router.get("/drivers/pending", response_model=list[PendingDriverResponse])
async def list_pending_drivers(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Get all drivers pending verification for admin review."""
    pending = driver_repo.get_pending_drivers(db)
    skip = (page - 1) * limit
    paginated = pending[skip : skip + limit]
    
    result = []
    for driver in paginated:
        docs = driver_document_repo.get_by_driver(db, driver.id)
        result.append({
            "id": driver.id,
            "name": driver.name,
            "email": driver.email,
            "phone": driver.phone,
            "vehicle_type": driver.vehicle_type,
            "vehicle_details": driver.vehicle_details,
            "service_area": driver.service_area,
            "verification_status": driver.verification_status,
            "created_at": driver.created_at,
            "documents_uploaded": len(docs) > 0,
            "documents_count": len(docs)
        })
    
    return result


@router.get("/drivers/{driver_id}/verification-status", response_model=DriverVerificationStatusResponse)
async def get_verification_status(
    driver_id: UUID,
    current_user = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Get driver verification status with all documents."""
    return driver_service.get_driver_verification_status(db, driver_id)


@router.put("/drivers/{driver_id}/approve")
async def approve_driver(
    driver_id: UUID,
    request: ApproveDriverRequest,
    current_user = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Approve a driver after document verification."""
    return driver_service.approve_driver(
        db,
        driver_id,
        current_user.id,
        request.notes
    )


@router.put("/drivers/{driver_id}/reject")
async def reject_driver(
    driver_id: UUID,
    request: RejectDriverRequest,
    current_user = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Reject a driver application."""
    return driver_service.reject_driver(
        db,
        driver_id,
        current_user.id,
        request.reason
    )


@router.put("/drivers/{driver_id}/suspend")
async def suspend_driver(
    driver_id: UUID,
    request: SuspendDriverRequest,
    current_user = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Suspend a previously approved driver."""
    return driver_service.suspend_driver(
        db,
        driver_id,
        current_user.id,
        request.reason
    )


@router.get("/drivers/{driver_id}/documents")
async def list_driver_documents(
    driver_id: UUID,
    current_user = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Get all documents uploaded by a driver for verification."""
    driver = driver_repo.get_by_id(db, driver_id)
    if not driver:
        raise NotFoundError("Driver not found")
    
    documents = driver_document_repo.get_by_driver(db, driver_id)
    return [
        {
            "id": str(doc.id),
            "document_type": doc.document_type,
            "file_name": doc.file_name,
            "file_size": doc.file_size,
            "file_type": doc.file_type,
            "status": doc.status,
            "uploaded_at": doc.uploaded_at,
            "verified_at": doc.verified_at,
            "expiry_date": doc.expiry_date
        }
        for doc in documents
    ]


# ===== STANDARD DRIVER MANAGEMENT (EXISTING) =====

@router.get("/drivers", response_model=list[DriverResponse])
async def list_all_drivers(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """List all drivers with pagination."""
    skip = (page - 1) * limit
    drivers = driver_repo.get_paginated(db, skip, limit)
    return drivers


@router.post("/drivers", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
async def create_new_driver(
    request: CreateDriverRequest,
    current_user = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Create a new driver (admin only - automatically approved)."""
    driver = driver_service.create_driver(db, request)
    return driver


@router.put("/drivers/{driver_id}", response_model=DriverResponse)
async def update_driver_info(
    driver_id: UUID,
    request: UpdateDriverRequest,
    current_user = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Update driver information."""
    driver = driver_service.update_driver(db, driver_id, request)
    return driver


@router.delete("/drivers/{driver_id}")
async def delete_driver(
    driver_id: UUID,
    current_user = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Deactivate a driver."""
    driver_service.deactivate_driver(db, driver_id)
    return {"message": "Driver deactivated successfully"}


@router.get("/drivers/{driver_id}/documents/{document_id}/download")
async def download_driver_document(
    driver_id: UUID,
    document_id: UUID,
    current_user = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Download a driver's uploaded document."""
    # Verify document belongs to driver
    doc = driver_document_repo.get_by_id(db, document_id)
    if not doc or doc.driver_id != driver_id:
        raise NotFoundError("Document not found")
    
    # Check file exists
    if not os.path.exists(doc.file_path):
        raise NotFoundError("File not found on server")
    
    # Return file
    return FileResponse(
        path=doc.file_path,
        filename=doc.file_name,
        media_type=f"application/{doc.file_type}" if doc.file_type == "pdf" else "image/*"
    )


@router.get("/users", response_model=list[UserResponse])
async def list_all_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """List all users with pagination."""
    skip = (page - 1) * limit
    users = user_repo.get_all(db, skip, limit)
    return users
