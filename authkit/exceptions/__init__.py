"""
Exposes the exceptions used within the AuthKit module.
"""
from .auth import (
    InvalidCredentialsError,
    InvalidOTPError,
    ConflictError,
    AuthError,
    NotFoundError,
    UserNotFoundError,
)

__all__ = [
    "InvalidCredentialsError",
    "InvalidOTPError",
    "ConflictError",
    "AuthError",
    "NotFoundError",
    "UserNotFoundError",
]
