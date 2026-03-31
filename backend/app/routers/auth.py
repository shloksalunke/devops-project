"""Authentication endpoints."""
from fastapi import APIRouter, Depends, status, Form, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest
from app.services import auth_service
from app.services.driver_service import register_driver as register_driver_service


router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new student user."""
    user, tokens = auth_service.register_student(db, request.name, request.email, request.password)
    return tokens


@router.post("/register-driver", status_code=status.HTTP_201_CREATED)
async def register_driver(
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    vehicle_type: str = Form(...),
    vehicle_details: str = Form(""),
    service_area: str = Form(""),
    id_document: UploadFile | None = File(None),
    license_document: UploadFile | None = File(None),
    rc_document: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    """Register a driver with RTO verification documents.
    
    Required documents:
    - id_document: Government ID (Aadhaar/PAN)
    - license_document: Driving License
    - rc_document: Vehicle Registration Certificate
    
    Driver starts with verification_status = PENDING and is hidden from search results.
    Admin must approve documents before driver becomes visible.
    """
    driver = register_driver_service(
        db,
        name=name,
        phone=phone,
        email=email,
        password=password,
        vehicle_type=vehicle_type,
        vehicle_details=vehicle_details if vehicle_details else None,
        service_area=service_area if service_area else None,
        id_document=id_document,
        license_document=license_document,
        rc_document=rc_document,
    )
    return {
        "message": "Driver registration submitted for verification. Await admin approval.",
        "driver_id": str(driver.id),
        "status": driver.verification_status
    }


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login a user or driver."""
    subject, tokens = auth_service.login(db, request.email, request.password)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: RefreshRequest, db: Session = Depends(get_db)):
    """Refresh access token."""
    tokens = auth_service.refresh_access_token(db, request.refresh_token)
    return tokens

