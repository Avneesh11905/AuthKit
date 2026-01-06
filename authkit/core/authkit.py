from authkit.core import Registry, Resolver
import authkit.usecases # Trigger registration
from .adapters import AuthAdapters
from authkit.ports import (
    UserRepository, UserReaderRepository, UserWriterRepository,
    PasswordManager, SessionService,
    OTPStore, OTPManager,
    RegistrationIntentStore, UserIDIntentStore
)
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import authkit.usecases


class AuthKit:
    """
    The main entry point for the AuthKit library.

    This Facade initializes all Use Cases with the provided adapters,
    exposing them as easily accessible properties.

    Usage (Unified Repository - Standard):
        >>> adapters = AuthAdapters(
        ...     user_repo=my_repo,
        ...     password_manager=my_pw_manager,
        ...     session_service=my_session_service
        ... )
        >>> auth = AuthKit(adapters)
        >>> auth.login.execute(...)

    Usage (CQRS - Split Repositories):
        >>> adapters = AuthAdapters(
        ...     user_reader=my_read_repo,
        ...     user_writer=my_write_repo,
        ...     password_manager=my_pw_manager,
        ...     session_service=my_session_service
        ... )
        >>> auth = AuthKit(adapters)
    """
    def __init__(
        self,
        # Make everything keyword-only for clarity and safety
        *,
        # Standard Repos
        user_repo: Optional[UserRepository] = None,
        # CQRS Repos (Alternative to user_repo)
        user_reader: Optional[UserReaderRepository] = None,
        user_writer: Optional[UserWriterRepository] = None,
        
        # Core Services
        password_manager: Optional[PasswordManager] = None,
        session_service: Optional[SessionService] = None,
        
        # OTP Services
        otp_store: Optional[OTPStore] = None,
        otp_manager: Optional[OTPManager] = None,
        
        # Intent Stores
        registration_intent_store: Optional[RegistrationIntentStore] = None,
        intent_store: Optional[UserIDIntentStore] = None,
        
        # Advanced: Pre-built adapters (Optional)
        adapters: Optional[AuthAdapters] = None,
    ):
        """
        Initialize the AuthKit facade with explicit dependency injections.
        
        Args:
            user_repo: Unified repository for both reading and writing (Simple mode).
            user_reader: Repository for reading user data (CQRS mode).
            user_writer: Repository for writing user data (CQRS mode).
            password_manager: Service for hashing and verifying passwords.
            session_service: Service for managing sessions/tokens.
            otp_store: Storage for OTP codes.
            otp_manager: Service for generating/validating OTPs.
            registration_intent_store: Storage for pending registrations.
            intent_store: Storage for user ID intents (e.g. forgot password).
            adapters: Pre-built AuthAdapters instance (Advanced).
        """
        if adapters:
             # Legacy/Advanced mode support
             pass
        else:
            # Collect all explicit args into a dict
            explicit_deps = {
                'user_repo': user_repo,
                'user_reader': user_reader,
                'user_writer': user_writer,
                'password_manager': password_manager,
                'session_service': session_service,
                'otp_store': otp_store,
                'otp_manager': otp_manager,
                'registration_intent_store': registration_intent_store,
                'intent_store': intent_store
            }
            # Remove None values so we don't overwrite defaults
            explicit_deps = {k: v for k, v in explicit_deps.items() if v is not None}
            
            # Merge with kwargs (custom extensions)
            final_kwargs = explicit_deps
            
            # Allow empty init (Partial/Template pattern)
            adapters = AuthAdapters(**final_kwargs)
            
        self._adapters = adapters
        
        # Explicit type hints for core use cases (for IDE autocomplete)
        # These are dynamically populated by the Registry loop below.
        self.login: 'authkit.usecases.LoginUseCase'
        self.register: 'authkit.usecases.RegistrationUseCase'
        self.logout: 'authkit.usecases.LogoutUseCase'
        self.logout_all: 'authkit.usecases.LogoutAllUseCase'
        self.change_password: 'authkit.usecases.ChangePasswordUseCase'
        self.delete_account: 'authkit.usecases.DeleteAccountUseCase'
        self.forget_password_start: 'authkit.usecases.StartForgetPasswordUseCase'
        self.forget_password_verify: 'authkit.usecases.VerifyForgetPasswordUseCase'
        self.login_otp_start: 'authkit.usecases.StartLoginWithOTPUseCase'
        self.login_otp_verify: 'authkit.usecases.VerifyLoginWithOTPUseCase'
        self.register_otp_start: 'authkit.usecases.StartRegistrationWithOTPUseCase'
        self.register_otp_verify: 'authkit.usecases.VerifyRegistrationWithOTPUseCase'
        self.logout_all_otp_start: 'authkit.usecases.StartLogoutAllWithOTPUseCase'
        self.logout_all_otp_verify: 'authkit.usecases.VerifyLogoutAllWithOTPUseCase'
        self.delete_account_otp_start: 'authkit.usecases.StartDeleteAccountWithOTPUseCase'
        self.delete_account_otp_verify: 'authkit.usecases.VerifyDeleteAccountWithOTPUseCase'
        
        # Dynamically instantiate all registered use cases
        self._rebind_use_cases()

    def configure(
        self, 
        # Repeating explicit args for DX
        user_repo: Optional[UserRepository] = None,
        user_reader: Optional[UserReaderRepository] = None,
        user_writer: Optional[UserWriterRepository] = None,
        password_manager: Optional[PasswordManager] = None,
        session_service: Optional[SessionService] = None,
        otp_store: Optional[OTPStore] = None,
        otp_manager: Optional[OTPManager] = None,
        registration_intent_store: Optional[RegistrationIntentStore] = None,
        intent_store: Optional[UserIDIntentStore] = None,
        **kwargs
    ):
        """
        Updates the current AuthKit instance with new dependencies.
        
        This method mutates the current instance. Use with caution in multi-threaded environments.
        
        Args:
            user_repo: Unified repository for both reading and writing.
            user_reader: Repository for reading user data.
            user_writer: Repository for writing user data.
            password_manager: Service for hashing and verifying passwords.
            session_service: Service for managing sessions/tokens.
            otp_store: Storage for OTP codes.
            otp_manager: Service for generating/validating OTPs.
            registration_intent_store: Storage for pending registrations.
            intent_store: Storage for user ID intents.
        """
        # Collect explicit args
        updates = {
            'user_repo': user_repo,
            'user_reader': user_reader,
            'user_writer': user_writer,
            'password_manager': password_manager,
            'session_service': session_service,
            'otp_store': otp_store,
            'otp_manager': otp_manager,
            'registration_intent_store': registration_intent_store,
            'intent_store': intent_store
        }
        # Filter None (meaning "no change")
        updates = {k: v for k, v in updates.items() if v is not None}
        
        # Merge with kwargs
        all_updates = {**updates, **kwargs}
        
        # FIX: If user_repo is updated, we must clear inferred reader/writer
        # to avoid "Ambiguous configuration" error in __post_init__.
        if 'user_repo' in all_updates:
            if 'user_reader' not in all_updates:
                setattr(self._adapters, 'user_reader', None)
            if 'user_writer' not in all_updates:
                setattr(self._adapters, 'user_writer', None)

        # Update existing adapters with new values
        for key, value in all_updates.items():
            setattr(self._adapters, key, value)
            
        # Re-run validation logic (optional but recommended)
        if hasattr(self._adapters, '__post_init__'):
            self._adapters.__post_init__()

        # CRITICAL: Re-instantiate use cases so they get the NEW dependencies.
        self._rebind_use_cases()
            
        return self

    def _rebind_use_cases(self):
        """Helper to instantiate/re-instantiate all use cases from the Registry."""
        for name, cls in Registry.items():
            try:
                instance = Resolver.resolve(cls, self._adapters)
                setattr(self, name, instance)
            except Exception as e:
                # Log warning but don't crash
                 pass
