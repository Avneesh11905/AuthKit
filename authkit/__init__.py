"""
The AuthKit module provides a comprehensive set of authentication and user management primitives.
"""
from authkit.ports import (
    UserReaderRepository,
    UserWriterRepository,
    RegistrationIntentStore,
    UserIDIntentStore,
    OTPManager,
    OTPStore,
    SessionService,
    Session,
    PasswordManager,
    UserRepository
)
from authkit.domain import (
    User,
    RegistrationIntent,
    OTPPurpose
)
from authkit.core.authkit import AuthKit

__all__ = [
    # Facade
    "AuthKit",

    # Entities
    "User", 
    "RegistrationIntent", 
    "OTPPurpose",

    # Ports
    "UserReaderRepository",
    "UserWriterRepository",
    "RegistrationIntentStore",
    "UserIDIntentStore",
    "OTPManager",
    "OTPStore",
    "SessionService",
    "Session",
    "PasswordManager",
    "UserRepository",
    # "SecurityEventPublisher",

]