from authkit.ports import UserRepository, SessionService, PasswordManager, UserIDIntentStore, RegistrationIntentStore
from authkit.ports.user_repo_cqrs import UserReaderRepository, UserWriterRepository


class AuthAdapters:
    """
    Dependency Injection container for AuthKit adapters.
    
    This class holds the concrete implementations of the abstract ports required by AuthKit.
    It supports two modes of operation for User Persistence:
    
    1. **Unified (Simple)**: specificy `user_repo`. The Facade will automatically set
       `user_reader` and `user_writer` to this same object.
    2. **CQRS (Advanced)**: specify `user_reader` and `user_writer` separately.
    
    Attributes:
        session_service: Service for issuing and verifying tokens (e.g. JWT, Database).
        password_manager: Service for hashing and verifying passwords.
        user_repo: (Optional) Unified repository implementing both Reader and Writer interfaces.
        user_reader: (Optional) Repository for reading user data.
        user_writer: (Optional) Repository for writing user data.
        otp_store: (Optional) For storing OTP codes.
        otp_manager: (Optional) For generating/validating OTPs.
        intent_store: (Optional) For storing Login/Recovery intents.
        registration_intent_store: (Optional) For storing Registration intents.
    """
    session_service: SessionService
    password_manager: PasswordManager
    
    user_repo: UserRepository | None = None
    
    user_reader: UserReaderRepository | None = None
    user_writer: UserWriterRepository | None = None
    
    intent_store: UserIDIntentStore | None = None
    registration_intent_store: RegistrationIntentStore | None = None

    # Allow dynamic extension via keyword arguments
    def __init__(self, session_service=None, password_manager=None, **kwargs):
        self.session_service = session_service
        self.password_manager = password_manager
        
        # Set optional known fields
        self.user_repo = kwargs.pop('user_repo', None)
        self.user_reader = kwargs.pop('user_reader', None)
        self.user_writer = kwargs.pop('user_writer', None)
        self.otp_store = kwargs.pop('otp_store', None)
        self.otp_manager = kwargs.pop('otp_manager', None)
        self.intent_store = kwargs.pop('intent_store', None)
        self.registration_intent_store = kwargs.pop('registration_intent_store', None)
        
        # Set any other custom dependencies (Extensions)
        for key, value in kwargs.items():
            setattr(self, key, value)
            
        # Run validation
        self.__post_init__()

    def __post_init__(self):
        if self.user_repo:
            if (self.user_reader is not None and self.user_reader is not self.user_repo) or \
               (self.user_writer is not None and self.user_writer is not self.user_repo):
                raise ValueError("Ambiguous configuration: Cannot provide 'user_repo' AND 'user_reader'/'user_writer'. Choose one mode.")
            
            self.user_reader = self.user_repo
            self.user_writer = self.user_repo
        
        # NOTE: We allow partial adapters now (e.g. for Factory usage), so we don't strictly enforce 
        # repo presence here. Missing repos will fail when Use Case is executed via MissingDependencyProxy.
