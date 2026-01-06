"""
Exposes fake implementations for testing.
"""
from .passwd_manager import FakePasswordManager
from .session_service import FakeSessionService
from .user_repo import FakeUserRepository
from .otp.otp_manager import FakeOTPManager
from .otp.otp_store import FakeOTPStore
from .intents.registration_intent_store import FakeRegistrationIntentStore
from .intents.user_id_intent_store import FakeUserIDIntentStore
from .user_repo_cqrs._reader import FakeUserReaderRepository
from .user_repo_cqrs._writer import FakeUserWriterRepository
from .user_repo_cqrs.user_store import FakeUserStore

__all__ = [
    "FakePasswordManager",
    "FakeSessionService",
    "FakeUserRepository",
    "FakeOTPManager",
    "FakeOTPStore",
    "FakeRegistrationIntentStore",
    "FakeUserIDIntentStore",
    "FakeUserReaderRepository",
    "FakeUserWriterRepository",
    "FakeUserStore",
]
