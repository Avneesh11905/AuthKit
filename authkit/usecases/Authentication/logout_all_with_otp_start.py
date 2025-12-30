from authkit.ports.user_repo_cqrs import UserReaderRepository
from authkit.ports.token_service import TokenService
from authkit.ports.otp.otp_store import OTPStore    
from authkit.ports.otp.otp_manager import OTPManager
from authkit.ports.intents.user_id_intent_store import UserIDIntentStore 
from authkit.domain import OTPPurpose 
from authkit.exceptions.auth import   InvalidCredentialsError
from uuid import  UUID

class StartLogoutAllWithOTPUseCase:
    """
    Use case to initiate global logout using OTP.
    """
    def __init__(self,
                 user_reader: UserReaderRepository,
                 token_service: TokenService,
                 intent_store: UserIDIntentStore,
                 otp_store: OTPStore,
                 otp_manager: OTPManager,
                 ):
        self.user_reader = user_reader
        self.token_service = token_service
        self.otp_store = otp_store
        self.otp_manager = otp_manager
        self.intent_store = intent_store

    async def execute(self, user_id: UUID) -> UUID:
        """
        Starts the global logout flow by sending an OTP.
        
        Args:
            user_id: The ID of the authenticated user.
            
        Returns:
            A UUID token representing the logout intent.
            
        Raises:
            InvalidCredentialsError: If the user is not found.
        """
        user = await self.user_reader.get_by_id(user_id)
        if not user:
            raise InvalidCredentialsError("User not found")
        logout_token = await self.intent_store.store(intent=user.id)
        otp = await self.otp_manager.generate()
        await self.otp_store.store(token=logout_token, 
                                   code=otp, 
                                   purpose=OTPPurpose.MFA)
        await self.otp_manager.send(identifier=user.identifier, 
                                    code=otp, 
                                    purpose=OTPPurpose.MFA)
        return logout_token