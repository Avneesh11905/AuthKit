from authkit.ports.intents.registration_intent_store import RegistrationIntentStore
from authkit.ports.otp.otp_store import OTPStore , OTPPurpose
from authkit.ports.user_repo_cqrs import UserWriterRepository
from authkit.exceptions.auth import InvalidOTPError 
from authkit.domain import User
from uuid import UUID , uuid4
from authkit.core import Registry

@Registry.register("register_otp_verify")
class VerifyRegistrationWithOTPUseCase:
    """
    Use case to verify registration OTP and create the user.
    """
    def __init__(self, 
                 user_writer: UserWriterRepository,
                 registration_intent_store: RegistrationIntentStore,
                 otp_store: OTPStore):
        self.registration_intent_store = registration_intent_store
        self.otp_store = otp_store
        self.user_writer = user_writer
    
    def execute(self, verification_token: UUID , code: str) -> User:
        """
        Verifies the OTP and creates the new user account.
        
        Args:
            verification_token: The intent token from the start flow.
            code: The OTP provided by the user.
            
        Returns:
            The newly created User object.
            
        Raises:
            InvalidOTPError: If OTP or intent is invalid.
        """
        intent = self.registration_intent_store.get(key=verification_token)
        if intent is None:
            raise InvalidOTPError("Intent not found")
        valid = self.otp_store.verify(token=verification_token, code=code, purpose=OTPPurpose.REGISTRATION)
        if not valid:
            raise InvalidOTPError("Invalid OTP")
        self.registration_intent_store.delete(key=verification_token)
        user = User(id=uuid4(),
                    identifier=intent.identifier,
                    password_hash=intent.password_hash,
                    credentials_version=intent.credentials_version,
                    metadata=intent.metadata)
        user = self.user_writer.add(user=user)
        return user
        
        