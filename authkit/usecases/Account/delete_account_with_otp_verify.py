from authkit.ports.session_service import SessionService
from authkit.ports.user_repo_cqrs import UserReaderRepository , UserWriterRepository
from authkit.ports.otp.otp_manager import OTPManager
from authkit.ports.otp.otp_store import OTPStore ,OTPPurpose
from authkit.ports.intents.user_id_intent_store import UserIDIntentStore
from uuid import UUID
from authkit.exceptions import InvalidOTPError ,InvalidCredentialsError
from authkit.core import Registry

@Registry.register("delete_account_otp_verify")
class VerifyDeleteAccountWithOTPUseCase:
    """
    Use case for verifying OTP and deleting account.
    """
    def __init__(self, 
                 user_reader: UserReaderRepository,
                 user_writer: UserWriterRepository,
                 session_service: SessionService,
                 intent_store: UserIDIntentStore,
                 otp_store: OTPStore,
                 otp_manager: OTPManager ):
        self.user_reader = user_reader
        self.user_writer = user_writer
        self.session_service = session_service
        self.otp_store = otp_store
        self.otp_manager = otp_manager
        self.intent_store = intent_store

    def execute(self, verification_token: UUID, code: str) -> UUID:

        """
        Verifies OTP and deletes the user account.
        
        Args:
            verification_token: The token received from start step.
            code: The OTP code provided by user.
            
        Returns:
            The ID of the deleted user.
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
            raise InvalidCredentialsError("User not found")
        self.session_service.revoke_all(user_id=user.id)
        self.user_writer.delete(user_id=user.id)
        return user.id
        