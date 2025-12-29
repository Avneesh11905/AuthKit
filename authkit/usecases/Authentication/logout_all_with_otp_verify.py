from authkit.ports.user_repo import UserRepository
from authkit.ports.token_service import TokenService
from authkit.ports.otp.otp_store import OTPStore    
from authkit.ports.intents.user_id_intent_store import UserIDIntentStore 
from authkit.exceptions.auth import InvalidOTPError
from authkit.domain import OTPPurpose
from uuid import UUID

class VerifyLogoutAllWithOTPUseCase:
    """
    Use case to verify OTP and execute global logout.
    """
    def __init__(self,
                 user_repo: UserRepository,
                 intent_store: UserIDIntentStore,
                 token_service: TokenService,
                 otp_store: OTPStore,
                 ):
        self.user_repo = user_repo
        self.intent_store = intent_store
        self.token_service = token_service
        self.otp_store = otp_store

    async def execute(self, logout_token: UUID, code: str) -> None:
        """
        Verifies the OTP and revokes all tokens for the user.
        
        Args:
            logout_token: The intent token from the start flow.
            code: The OTP provided by the user.
            
        Raises:
            InvalidOTPError: If OTP or intent is invalid.
        """
        intent = await self.intent_store.get(key=logout_token)
        if intent is None:
            raise InvalidOTPError("Intent not found")
        valid = await self.otp_store.verify(token=logout_token, 
                                    purpose=OTPPurpose.MFA, 
                                    code=code)
        if not valid:
            raise InvalidOTPError("Invalid OTP")
        await self.intent_store.delete(key=logout_token)
        await self.token_service.revoke_all(user_id=intent)
        await self.user_repo.increment_credentials_version(user_id=intent)
