from authkit.ports.otp.otp_manager import OTPManager
from authkit.ports.otp.otp_store import OTPStore
from authkit.ports.user_repo_cqrs import UserReaderRepository
from authkit.ports.passwd_manager import PasswordManager
from authkit.ports.intents.user_id_intent_store import  UserIDIntentStore
from authkit.exceptions.auth import InvalidCredentialsError 
from authkit.domain import OTPPurpose
from uuid import UUID


from authkit.core import Registry

@Registry.register("login_otp_start")
class StartLoginWithOTPUseCase:
    """
    Use case to initiate login with OTP (MFA).
    """
    def __init__(
        self,
        user_reader: UserReaderRepository,
        password_manager: PasswordManager,
        intent_store: UserIDIntentStore,
        otp_store: OTPStore,
        otp_manager: OTPManager,
    ):
        self.user_reader = user_reader
        self.password_manager = password_manager
        self.otp_store = otp_store
        self.otp_manager = otp_manager
        self.intent_store = intent_store

    def execute(self, identifier: str, password: str) -> UUID:
        """
        Validates credentials and starts the OTP login flow.
        
        Args:
            identifier: The user's identifier.
            password: The user's password.
            
        Returns:
            A UUID token representing the verification intent.
            
        Raises:
            InvalidCredentialsError: If credentials are invalid.
        """
        user = self.user_reader.get_by_identifier(identifier=identifier)
        if not user:
            raise InvalidCredentialsError("User not found")
        if not self.password_manager.verify(password=password, 
                                                    hashed_password=user.password_hash):
            raise InvalidCredentialsError("Invalid password")
        verification_token = self.intent_store.store(intent=user.id)
        otp = self.otp_manager.generate()
        self.otp_store.store(token=verification_token,
                                   code=otp,
                                   purpose=OTPPurpose.MFA)
        self.otp_manager.send(identifier=identifier,
                                    code=otp,
                                    purpose=OTPPurpose.MFA)
        return verification_token