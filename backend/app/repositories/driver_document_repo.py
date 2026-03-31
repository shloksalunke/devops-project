"""Driver document repository."""
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.driver_document import DriverDocument


def create(db: Session, **fields) -> DriverDocument:
    """Create a new driver document record."""
    doc = DriverDocument(**fields)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def get_by_id(db: Session, doc_id: UUID) -> DriverDocument | None:
    """Get document by ID."""
    return db.query(DriverDocument).filter(DriverDocument.id == doc_id).first()


def get_by_driver(db: Session, driver_id: UUID) -> list[DriverDocument]:
    """Get all documents for a driver."""
    return db.query(DriverDocument).filter(DriverDocument.driver_id == driver_id).all()


def get_by_driver_and_type(db: Session, driver_id: UUID, document_type: str) -> DriverDocument | None:
    """Get specific document type for a driver."""
    return db.query(DriverDocument).filter(
        DriverDocument.driver_id == driver_id,
        DriverDocument.document_type == document_type
    ).first()


def get_pending_for_driver(db: Session, driver_id: UUID) -> list[DriverDocument]:
    """Get all pending documents for a driver."""
    return db.query(DriverDocument).filter(
        DriverDocument.driver_id == driver_id,
        DriverDocument.status == "PENDING"
    ).all()


def update(db: Session, doc_id: UUID, **fields) -> DriverDocument:
    """Update document fields."""
    doc = get_by_id(db, doc_id)
    if doc:
        for key, value in fields.items():
            if value is not None and hasattr(doc, key):
                setattr(doc, key, value)
        db.commit()
        db.refresh(doc)
    return doc


def approve(db: Session, doc_id: UUID, verified_by: UUID) -> DriverDocument:
    """Approve a document."""
    import datetime
    from sqlalchemy.sql import func
    return update(db, doc_id, status="APPROVED", verified_by=verified_by, verified_at=datetime.datetime.now(datetime.timezone.utc))


def reject(db: Session, doc_id: UUID, rejection_reason: str, verified_by: UUID) -> DriverDocument:
    """Reject a document."""
    import datetime
    return update(db, doc_id, status="REJECTED", rejection_reason=rejection_reason, verified_by=verified_by, verified_at=datetime.datetime.now(datetime.timezone.utc))


def delete(db: Session, doc_id: UUID) -> bool:
    """Delete a document."""
    doc = get_by_id(db, doc_id)
    if doc:
        db.delete(doc)
        db.commit()
        return True
    return False


def all_approved(db: Session, driver_id: UUID) -> bool:
    """Check if all required documents for a driver are approved."""
    required_docs = ['ID', 'LICENSE', 'RC']
    for doc_type in required_docs:
        doc = get_by_driver_and_type(db, driver_id, doc_type)
        if not doc or doc.status != "APPROVED":
            return False
    return True
