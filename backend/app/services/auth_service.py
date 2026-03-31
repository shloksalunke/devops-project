"""Authentication service."""
from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.config import settings
from app.exceptions import UnauthorizedError, ConflictError
from app.repositories import user_repo, driver_repo
from app.schemas.auth import TokenResponse


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain password against a hash."""
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode a JWT token and return payload."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise UnauthorizedError("Invalid or expired token")


def register_student(db: Session, name: str, email: str, password: str) -> tuple:
    """Register a new student user."""
    # Check if email already exists
    existing_user = user_repo.get_by_email(db, email)
    if existing_user:
        raise ConflictError("Email already registered")

    # Hash password and create user
    hashed_password = hash_password(password)
    user = user_repo.create(db, name=name, email=email, hashed_password=hashed_password, role="student")

    # Generate tokens
    access_token = create_access_token({"sub": str(user.id), "type": "user"})
    refresh_token = create_refresh_token({"sub": str(user.id), "type": "user"})

    return user, TokenResponse(access_token=access_token, refresh_token=refresh_token)


def login(db: Session, email: str, password: str) -> tuple:
    """Login user or driver."""
    # Try to find user first
    user = user_repo.get_by_email(db, email)
    if user:
        if not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedError("User is inactive")

        access_token = create_access_token({"sub": str(user.id), "type": "user"})
        refresh_token = create_refresh_token({"sub": str(user.id), "type": "user"})
        return user, TokenResponse(access_token=access_token, refresh_token=refresh_token)

    # Try to find driver
    driver = driver_repo.get_by_email(db, email)
    if driver:
        if not verify_password(password, driver.hashed_password):
            raise UnauthorizedError("Invalid email or password")
        if not driver.is_active:
            raise UnauthorizedError("Driver is inactive")

        access_token = create_access_token({"sub": str(driver.id), "type": "driver"})
        refresh_token = create_refresh_token({"sub": str(driver.id), "type": "driver"})
        return driver, TokenResponse(access_token=access_token, refresh_token=refresh_token)

    raise UnauthorizedError("Invalid email or password")


def refresh_access_token(db: Session, refresh_token: str) -> TokenResponse:
    """Refresh access token."""
    payload = decode_token(refresh_token)
    user_id = UUID(payload.get("sub"))
    user_type = payload.get("type")

    if user_type == "user":
        user = user_repo.get_by_id(db, user_id)
        if not user or not user.is_active:
            raise UnauthorizedError("User not found or inactive")
        new_access_token = create_access_token({"sub": str(user.id), "type": "user"})
    elif user_type == "driver":
        driver = driver_repo.get_by_id(db, user_id)
        if not driver or not driver.is_active:
            raise UnauthorizedError("Driver not found or inactive")
        new_access_token = create_access_token({"sub": str(driver.id), "type": "driver"})
    else:
        raise UnauthorizedError("Invalid token type")

    return TokenResponse(access_token=new_access_token, refresh_token=refresh_token)
