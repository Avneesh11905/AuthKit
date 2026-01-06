class AuthError(Exception):
    """Base class for all authentication-related exceptions."""
    ...

class InvalidCredentialsError(AuthError):
    """Raised when authentication fails due to incorrect credentials."""
    ...

class ConflictError(AuthError):
    """Raised when an operation conflicts with existing state (e.g., duplicate user)."""
    ...

class InvalidOTPError(AuthError):
    """Raised when an OTP is invalid or expired."""
    ...

class NotFoundError(AuthError):
    """Raised when a requested resource is not found."""
    ...

class UserNotFoundError(NotFoundError):
    """Raised specifically when a user is not found."""
    ...

class FeatureNotConfiguredError(AuthError):
    """Raised when a feature cannot be used because its dependencies are missing."""
    ...