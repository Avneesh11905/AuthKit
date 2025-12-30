from authkit.ports.intents.registration_intent_store import RegistrationIntentStore
from authkit.ports.otp.otp_store import OTPStore , OTPPurpose
from authkit.ports.otp.otp_manager import OTPManager
from authkit.ports.user_repo_cqrs import UserReaderRepository
from authkit.ports.passwd_manager import PasswordManager
from authkit.exceptions.auth import ConflictError
from authkit.domain import  RegistrationIntent
from uuid import UUID

class StartRegistrationWithOTPUseCase:
    """
    Use case to initiate registration with OTP verification.
    """
    def __init__(self, 
                 user_reader: UserReaderRepository,
                 password_store: PasswordManager,
                 intent_store: RegistrationIntentStore,
                 otp_store: OTPStore,
                 otp_manager: OTPManager):
        self.user_reader = user_reader
        self.password_store = password_store
        self.intent_store = intent_store
        self.otp_store = otp_store
        self.otp_manager = otp_manager
        self.otp_purpose = OTPPurpose.REGISTRATION

    async def execute(self, identifier: str, password: str) -> UUID:
        """
        Validates new user details and sends a verification OTP.
        
        Args:
            identifier: The user's identifier.
            password: The user's password.
            
        Returns:
            A UUID token representing the registration intent.
            
        Raises:
            ConflictError: If the user already exists.
        """
        if await self.user_reader.get_by_identifier(identifier=identifier):
            raise ConflictError("User already exists")
        hashed_password = await self.password_store.hash(password=password)
        intent = RegistrationIntent(identifier=identifier,
                                    password_hash=hashed_password,
                                    credentials_version=0)
        token =  await self.intent_store.store(intent=intent)
        otp = await self.otp_manager.generate()
        await self.otp_store.store(token=token, code=otp, purpose=self.otp_purpose)
        await self.otp_manager.send(identifier=identifier, code=otp, purpose=self.otp_purpose)
        return token