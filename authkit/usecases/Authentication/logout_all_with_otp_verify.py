from authkit.ports.user_repo_cqrs import UserWriterRepository
from authkit.ports.session_service import AuthSessionService
from authkit.ports.otp.otp_store import OTPStore    
from authkit.ports.intents.user_id_intent_store import UserIDIntentStore 
from authkit.exceptions.auth import InvalidOTPError
from authkit.domain import OTPPurpose
from uuid import UUID

from authkit.core import Registry

@Registry.register("logout_all_otp_verify")
class VerifyLogoutAllWithOTPUseCase:
    """
    Use case to verify OTP and execute global logout.
    """
    def __init__(self,
                 user_writer: UserWriterRepository,
                 intent_store: UserIDIntentStore,
                 session_service: AuthSessionService,
                 otp_store: OTPStore,
                 ):
        self.user_writer = user_writer
        self.intent_store = intent_store
        self.session_service = session_service
        self.otp_store = otp_store

    def execute(self, logout_token: UUID, code: str) -> None:
        """
        Verifies the OTP and revokes all tokens for the user.
        
        Args:
            logout_token: The intent token from the start flow.
            code: The OTP provided by the user.
            
        Raises:
            InvalidOTPError: If OTP or intent is invalid.
        """
        intent = self.intent_store.get(key=logout_token)
        if intent is None:
            raise InvalidOTPError("Intent not found")
        valid = self.otp_store.verify(token=logout_token, 
                                    purpose=OTPPurpose.MFA, 
                                    code=code)
        if not valid:
            raise InvalidOTPError("Invalid OTP")
        self.intent_store.delete(key=logout_token)
        self.session_service.revoke_all(user_id=intent)
        self.user_writer.increment_credentials_version(user_id=intent)
