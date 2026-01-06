from authkit.ports.session_service import SessionService
from authkit.ports.user_repo_cqrs import UserReaderRepository , UserWriterRepository
from authkit.ports.otp.otp_manager import OTPManager
from authkit.ports.otp.otp_store import OTPStore ,OTPPurpose
from authkit.ports.intents.user_id_intent_store import UserIDIntentStore
from uuid import UUID
from authkit.exceptions import InvalidCredentialsError
from authkit.core import Registry

@Registry.register("delete_account_otp_start")
class StartDeleteAccountWithOTPUseCase:
    """
    Use case for initiating account deletion with OTP.
    """
    def __init__(self, 
                 user_reader: UserReaderRepository,
                 intent_store: UserIDIntentStore,
                 otp_store: OTPStore,
                 otp_manager: OTPManager ):
        self.user_reader = user_reader
        self.otp_store = otp_store
        self.otp_manager = otp_manager
        self.intent_store = intent_store

    def execute(self, user_id: UUID) -> UUID:
        """
        Deletes the user account and revokes all associated tokens.
        
        Args:
            user_id: The ID of the user to delete.
            
        Returns:
            The verification token (UUID) to be used in the verify step.
        """
        user = self.user_reader.get_by_id(user_id)
        if user is None:
            raise InvalidCredentialsError("User not found")
        verification_token = self.intent_store.store(intent=user.id)
        otp = self.otp_manager.generate()
        self.otp_store.store(token=verification_token,
                                   code=otp,
                                   purpose=OTPPurpose.MFA)
        self.otp_manager.send(identifier=user.identifier,
                                    code=otp,
                                    purpose=OTPPurpose.MFA)
        return verification_token