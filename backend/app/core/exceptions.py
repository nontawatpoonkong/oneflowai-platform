"""Application-level exceptions.

Services raise these; a single handler (registered in `main`) maps them to
the standard error response envelope. This keeps HTTP concerns out of the
service layer.
"""

from typing import Any


class AppError(Exception):
    """Base application error."""

    status_code: int = 400
    code: str = "BAD_REQUEST"
    message: str = "Bad request"

    def __init__(self, message: str | None = None, details: Any | None = None) -> None:
        self.message = message or self.message
        self.details = details
        super().__init__(self.message)


class EmailAlreadyExistsError(AppError):
    status_code = 409
    code = "EMAIL_ALREADY_EXISTS"
    message = "A user with this email already exists"


class InvalidCredentialsError(AppError):
    status_code = 401
    code = "INVALID_CREDENTIALS"
    message = "Invalid email or password"


class AuthenticationError(AppError):
    status_code = 401
    code = "UNAUTHENTICATED"
    message = "Not authenticated"


class InactiveUserError(AppError):
    status_code = 403
    code = "INACTIVE_USER"
    message = "User account is inactive"


class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"
    message = "Resource not found"
