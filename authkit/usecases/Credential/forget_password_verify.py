from authkit.ports.user_repo import UserRepository
from authkit.ports.token_service import TokenService
from authkit.ports.otp.otp_store import OTPStore    
from authkit.ports.otp.otp_manager import OTPManager
from authkit.ports.passwd_manager import PasswordManager
from authkit.ports.intents.user_id_intent_store import UserIDIntentStore
from authkit.domain import OTPPurpose
from authkit.exceptions import InvalidOTPError
from uuid import UUID

class VerifyForgetPasswordUseCase:
    """
    Use case to complete the password recovery process.
    """
    def __init__(self,
                 user_repo: UserRepository,
                 token_service: TokenService,
                 password_manager: PasswordManager,
                 intent_store: UserIDIntentStore,
                 otp_store: OTPStore,
                 otp_manager: OTPManager):
        self.user_repo = user_repo
        self.token_service = token_service
        self.otp_store = otp_store
        self.otp_manager = otp_manager
        self.password_manager = password_manager
        self.intent_store = intent_store

    async def execute(self, forget_token: UUID, code: str , new_password: str) -> None:
        """
        Verifies the recovery OTP and updates the password.
        
        Args:
            forget_token: The intent token returned by the start use case.
            code: The OTP code provided by the user.
            new_password: The new password to set.
            
        Raises:
            InvalidOTPError: If the OTP or intent is invalid.
        """
        intent = await self.intent_store.get(key=forget_token)
        if intent is None:
            raise InvalidOTPError("Intent not found")
        valid = await self.otp_store.verify(token=forget_token, 
                                    purpose=OTPPurpose.FORGET_PASSWORD, 
                                    code=code)
        if not valid:
            raise InvalidOTPError("Invalid OTP")
        await self.intent_store.delete(key=forget_token)
        await self.token_service.revoke_all(user_id=intent)
        await self.user_repo.increment_credentials_version(user_id=intent)
        hashed_password = await self.password_manager.hash(password=new_password)
        await self.user_repo.change_password(user_id=intent, new_password_hash=hashed_password)
