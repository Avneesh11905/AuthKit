from authkit.ports.otp.otp_store import OTPStore
from authkit.ports.user_repo import UserRepository
from authkit.ports.token_service import TokenService , Token
from authkit.ports.intents.user_id_intent_store import UserIDIntentStore 
from authkit.exceptions.auth import InvalidOTPError
from authkit.domain import OTPPurpose
from uuid import UUID

class VerifyLoginWithOTPUseCase:
    """
    Use case to verify OTP and complete login.
    """
    def __init__(
        self,
        user_repo: UserRepository,
        intent_store: UserIDIntentStore,
        token_service: TokenService,
        otp_store: OTPStore,
    ):
        self.user_repo = user_repo
        self.token_service = token_service
        self.otp_store = otp_store
        self.intent_store = intent_store

    async def execute(self, verification_token: UUID, code: str) -> Token:
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
        intent = await self.intent_store.get(key=verification_token)
        if intent is None:
            raise InvalidOTPError("Intent not found")
        valid = await self.otp_store.verify(token=verification_token,
                                            purpose=OTPPurpose.MFA,
                                            code=code)
        if not valid:
            raise InvalidOTPError("Invalid OTP")
        await self.intent_store.delete(key=verification_token)
        user = await self.user_repo.get_by_id(user_id=intent)
        if not user:
            raise InvalidOTPError("User not found")
        auth_token = await self.token_service.issue(user_id=user.id,
                                                    credential_version=user.credentials_version)
        await self.user_repo.update_last_login(user_id=user.id)
        return auth_token
