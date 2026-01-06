from typing import Optional
from authkit.core.adapters import AuthAdapters
from authkit.ports import (
    UserRepository, UserReaderRepository, UserWriterRepository,
    PasswordManager, SessionService,
    OTPStore, OTPManager,
    RegistrationIntentStore, UserIDIntentStore
)
import authkit.usecases

class AuthKit:
    """
    The main entry point for the AuthKit library.
    """
    login: authkit.usecases.LoginUseCase
    register: authkit.usecases.RegistrationUseCase
    logout: authkit.usecases.LogoutUseCase
    logout_all: authkit.usecases.LogoutAllUseCase
    change_password: authkit.usecases.ChangePasswordUseCase
    delete_account: authkit.usecases.DeleteAccountUseCase
    forget_password_start: authkit.usecases.StartForgetPasswordUseCase
    forget_password_verify: authkit.usecases.VerifyForgetPasswordUseCase
    login_otp_start: authkit.usecases.StartLoginWithOTPUseCase
    login_otp_verify: authkit.usecases.VerifyLoginWithOTPUseCase
    register_otp_start: authkit.usecases.StartRegistrationWithOTPUseCase
    register_otp_verify: authkit.usecases.VerifyRegistrationWithOTPUseCase
    logout_all_otp_start: authkit.usecases.StartLogoutAllWithOTPUseCase
    logout_all_otp_verify: authkit.usecases.VerifyLogoutAllWithOTPUseCase
    delete_account_otp_start: authkit.usecases.StartDeleteAccountWithOTPUseCase
    delete_account_otp_verify: authkit.usecases.VerifyDeleteAccountWithOTPUseCase

    def __init__(
        self,
        *,
        user_repo: Optional[UserRepository] = None,
        user_reader: Optional[UserReaderRepository] = None,
        user_writer: Optional[UserWriterRepository] = None,
        password_manager: Optional[PasswordManager] = None,
        session_service: Optional[SessionService] = None,
        otp_store: Optional[OTPStore] = None,
        otp_manager: Optional[OTPManager] = None,
        registration_intent_store: Optional[RegistrationIntentStore] = None,
        intent_store: Optional[UserIDIntentStore] = None,
        adapters: Optional[AuthAdapters] = None,
    ) -> None: ...

    def configure(
        self,
        user_repo: Optional[UserRepository] = None,
        user_reader: Optional[UserReaderRepository] = None,
        user_writer: Optional[UserWriterRepository] = None,
        password_manager: Optional[PasswordManager] = None,
        session_service: Optional[SessionService] = None,
        otp_store: Optional[OTPStore] = None,
        otp_manager: Optional[OTPManager] = None,
        registration_intent_store: Optional[RegistrationIntentStore] = None,
        intent_store: Optional[UserIDIntentStore] = None,
    ) -> "AuthKit": ...
