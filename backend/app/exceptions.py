"""Custom application exceptions."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


class AppException(Exception):
    """Base application exception."""
    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(AppException):
    """Resource not found exception."""
    status_code = 404
    error_code = "NOT_FOUND"


class UnauthorizedError(AppException):
    """Authentication failed exception."""
    status_code = 401
    error_code = "UNAUTHORIZED"


class ForbiddenError(AppException):
    """Permission denied exception."""
    status_code = 403
    error_code = "FORBIDDEN"


class ConflictError(AppException):
    """Resource conflict exception."""
    status_code = 409
    error_code = "CONFLICT"


class BadRequestError(AppException):
    """Invalid request exception."""
    status_code = 400
    error_code = "BAD_REQUEST"


class DatabaseError(AppException):
    """Database operation exception."""
    status_code = 500
    error_code = "DATABASE_ERROR"


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the app."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code,
                "message": exc.message,
                "status_code": exc.status_code,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "status_code": 500,
            },
        )
