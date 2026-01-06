from authkit.ports.intents.registration_intent_store import RegistrationIntentStore
from authkit.ports.otp.otp_store import OTPStore , OTPPurpose
from authkit.ports.otp.otp_manager import OTPManager
from authkit.ports.user_repo_cqrs import UserReaderRepository
from authkit.ports.passwd_manager import PasswordManager
from authkit.exceptions.auth import ConflictError
from authkit.domain import  RegistrationIntent
from uuid import UUID, uuid4

from authkit.core import Registry

@Registry.register("register_otp_start")
class StartRegistrationWithOTPUseCase:
    """
    Use case to initiate registration with OTP verification.
    """
    def __init__(self, 
                 user_reader: UserReaderRepository,
                 password_manager: PasswordManager,
                 registration_intent_store: RegistrationIntentStore,
                 otp_store: OTPStore,
                 otp_manager: OTPManager):
        self.user_reader = user_reader
        self.password_manager = password_manager
        self.registration_intent_store = registration_intent_store
        self.otp_store = otp_store
        self.otp_manager = otp_manager
        self.otp_purpose = OTPPurpose.REGISTRATION

    def execute(self, identifier: str, password: str) -> UUID:
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
        if self.user_reader.get_by_identifier(identifier=identifier):
            raise ConflictError("User already exists")
        hashed_password = self.password_manager.hash(password=password)
        
        # Create intent (no ID or OTP code here, as per domain definition)
        intent = RegistrationIntent(
            identifier=identifier,
            password_hash=hashed_password,
            credentials_version=0
        )
        
        # Store intent to get the token (ID)
        token = self.registration_intent_store.store(intent=intent)
        
        # Generate and store OTP
        otp_code = self.otp_manager.generate()
        self.otp_store.store(token=token, code=otp_code, purpose=self.otp_purpose)
        self.otp_manager.send(identifier=identifier, code=otp_code, purpose=self.otp_purpose)
        
        return token
