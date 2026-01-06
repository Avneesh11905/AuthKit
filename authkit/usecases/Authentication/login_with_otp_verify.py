from authkit.ports.otp.otp_store import OTPStore
from authkit.ports.user_repo_cqrs import UserReaderRepository , UserWriterRepository
from authkit.ports.session_service import SessionService ,Session
from authkit.ports.intents.user_id_intent_store import UserIDIntentStore 
from authkit.exceptions.auth import InvalidOTPError
from authkit.domain import OTPPurpose
from uuid import UUID

from authkit.core import Registry

@Registry.register("login_otp_verify")
class VerifyLoginWithOTPUseCase:
    """
    Use case to verify OTP and complete login using CQRS pattern.
    """
    def __init__(
        self,
        user_reader: UserReaderRepository,
        user_writer: UserWriterRepository,
        intent_store: UserIDIntentStore,
        session_service: SessionService,
        otp_store: OTPStore,
    ):
        self.user_reader = user_reader
        self.user_writer = user_writer
        self.session_service = session_service
        self.otp_store = otp_store
        self.intent_store = intent_store

    def execute(self, verification_token: UUID, code: str) -> Session:
        """
        Verifies the OTP and issues an authentication token.
        
        Args:
            verification_token: The intent token from the start flow.
            code: The OTP provided by the user.
            
        Returns:
            A Token object.
            
        Raises:
            InvalidOTPError: If OTP or intent is invalid.
        """
        intent = self.intent_store.get(key=verification_token)
        if intent is None:
            raise InvalidOTPError("Intent not found")
        valid = self.otp_store.verify(token=verification_token,
                                            purpose=OTPPurpose.MFA,
                                            code=code)
        if not valid:
            raise InvalidOTPError("Invalid OTP")
        self.intent_store.delete(key=verification_token)
        user = self.user_reader.get_by_id(user_id=intent)
        if not user:
            raise InvalidOTPError("User not found")
        auth_token = self.session_service.issue(user_id=user.id,
                                                    credential_version=user.credentials_version)
        self.user_writer.update_last_login(user_id=user.id)
        return auth_token
