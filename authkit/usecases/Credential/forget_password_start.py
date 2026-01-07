from authkit.ports.user_repo_cqrs import UserReaderRepository
from authkit.ports.otp.otp_store import OTPStore    
from authkit.ports.otp.otp_manager import OTPManager
from authkit.ports.intents.user_id_intent_store import UserIDIntentStore
from authkit.domain import OTPPurpose 
from authkit.exceptions.auth import NotFoundError
from uuid import  UUID

from authkit.core import Registry

@Registry.register("forget_password_start")
class StartForgetPasswordUseCase:
    """
    Use case to initiate the password recovery process.
    """
    def __init__(self,
                 user_reader: UserReaderRepository,
                 otp_store: OTPStore,
                 otp_manager: OTPManager,
                 intent_store: UserIDIntentStore):
        self.user_reader = user_reader
        self.otp_store = otp_store
        self.otp_manager = otp_manager
        self.intent_store = intent_store

    def execute(self, identifier: str) -> UUID:
        """
        Starts the password recovery flow.
        
        Generates an OTP and temporarily stores the user's intent.
        
        Args:
            identifier: The user's identifier (email/username).
            
        Returns:
            A UUID token representing the recovery intent.
            
        Raises:
            NotFoundError: If the user does not exist.
        """
        user = self.user_reader.get_by_identifier(identifier)
        if not user:
            raise NotFoundError("User not found")
        forget_token = self.intent_store.store(intent=user.id)
        otp = self.otp_manager.generate()
        self.otp_store.store(token=forget_token, 
                                   code=otp, 
                                   purpose=OTPPurpose.FORGET_PASSWORD)
        self.otp_manager.send(identifier=identifier, 
                                    code=otp, 
                                    metadata=user.metadata,
                                    purpose=OTPPurpose.FORGET_PASSWORD)
        return forget_token