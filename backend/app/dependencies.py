"""Application dependencies."""
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.services.auth_service import decode_token
from app.repositories.user_repo import get_by_id as get_user_by_id
from app.repositories.driver_repo import get_by_id as get_driver_by_id
from app.exceptions import UnauthorizedError, ForbiddenError


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Dependency to get current authenticated user (student or driver)."""
    payload = decode_token(token)
    user_type = payload.get("type")
    user_id: UUID = UUID(payload.get("sub"))

    if user_type == "user":
        user = get_user_by_id(db, user_id)
        if not user:
            raise UnauthorizedError("User not found")
        if not user.is_active:
            raise UnauthorizedError("User is inactive")
        user.role = user.role
        return user

    elif user_type == "driver":
        driver = get_driver_by_id(db, user_id)
        if not driver:
            raise UnauthorizedError("Driver not found")
        driver.role = "driver"
        return driver

    raise UnauthorizedError("Invalid token")


def require_role(*roles: str):
    """Dependency factory to enforce role-based access control."""
    async def check_role(current_user = Depends(get_current_user)):
        user_role = getattr(current_user, "role", None)
        if user_role not in roles:
            raise ForbiddenError("You do not have permission")
        return current_user

    return check_role
