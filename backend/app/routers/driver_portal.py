"""Driver portal endpoints."""
import os
from uuid import UUID
from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_role
from app.schemas.driver import DriverResponse, UpdateDriverRequest, AvailabilityRequest
from app.schemas.rating import RatingResponse
from app.services import driver_service, rating_service
from app.repositories import driver_repo, driver_document_repo
from app.exceptions import NotFoundError


router = APIRouter()


@router.get("/me", response_model=DriverResponse)
async def get_driver_profile(
    current_user = Depends(require_role("driver")),
    db: Session = Depends(get_db)
):
    """Get current driver profile."""
    return current_user


@router.put("/me", response_model=DriverResponse)
async def update_driver_profile(
    request: UpdateDriverRequest,
    current_user = Depends(require_role("driver")),
    db: Session = Depends(get_db)
):
    """Update driver profile."""
    driver = driver_service.update_driver(db, current_user.id, request)
    return driver


@router.put("/me/availability", status_code=status.HTTP_200_OK)
async def set_driver_availability(
    request: AvailabilityRequest,
    current_user = Depends(require_role("driver")),
    db: Session = Depends(get_db)
):
    """Set driver availability."""
    driver_service.set_availability(db, current_user.id, request.is_available)
    return {"is_available": request.is_available}


@router.get("/me/ratings", response_model=list[RatingResponse])
async def get_driver_ratings(
    current_user = Depends(require_role("driver")),
    db: Session = Depends(get_db)
):
    """Get ratings for current driver."""
    ratings = rating_service.get_driver_ratings(db, current_user.id)
    return ratings


@router.get("/me/verification-status")
async def get_verification_status(
    current_user = Depends(require_role("driver")),
    db: Session = Depends(get_db)
):
    """Get driver verification status with all documents."""
    driver = current_user
    documents = driver_document_repo.get_by_driver(db, driver.id)

    return {
        "driver_id": str(driver.id),
        "verification_status": driver.verification_status,
        "documents": [
            {
                "id": str(doc.id),
                "document_type": doc.document_type,
                "file_name": doc.file_name,
                "file_size": doc.file_size,
                "file_type": doc.file_type,
                "status": doc.status,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
                "verified_at": doc.verified_at.isoformat() if doc.verified_at else None,
                "expiry_date": doc.expiry_date.isoformat() if doc.expiry_date else None,
                "rejection_reason": doc.rejection_reason
            }
            for doc in documents
        ]
    }


@router.get("/me/documents")
async def list_my_documents(
    current_user = Depends(require_role("driver")),
    db: Session = Depends(get_db)
):
    """List all documents uploaded by the current driver."""
    documents = driver_document_repo.get_by_driver(db, current_user.id)
    return [
        {
            "id": str(doc.id),
            "document_type": doc.document_type,
            "file_name": doc.file_name,
            "file_size": doc.file_size,
            "file_type": doc.file_type,
            "status": doc.status,
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
            "verified_at": doc.verified_at.isoformat() if doc.verified_at else None,
            "expiry_date": doc.expiry_date.isoformat() if doc.expiry_date else None,
            "rejection_reason": doc.rejection_reason
        }
        for doc in documents
    ]


@router.get("/me/documents/{document_id}/download")
async def download_my_document(
    document_id: UUID,
    current_user = Depends(require_role("driver")),
    db: Session = Depends(get_db)
):
    """Download one of the current driver's uploaded documents."""
    doc = driver_document_repo.get_by_id(db, document_id)
    if not doc or doc.driver_id != current_user.id:
        raise NotFoundError("Document not found")

    if not os.path.exists(doc.file_path):
        raise NotFoundError("File not found on server")

    return FileResponse(
        path=doc.file_path,
        filename=doc.file_name,
        media_type=f"application/{doc.file_type}" if doc.file_type == "pdf" else "image/*"
    )