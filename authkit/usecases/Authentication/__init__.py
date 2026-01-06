"""
Use cases for authentication flows (login, logout, registration).
"""
from authkit.usecases.Authentication.login import LoginUseCase
from authkit.usecases.Authentication.login_with_otp_start import StartLoginWithOTPUseCase
from authkit.usecases.Authentication.login_with_otp_verify import VerifyLoginWithOTPUseCase
from authkit.usecases.Authentication.logout import LogoutUseCase
from authkit.usecases.Authentication.logout_all import LogoutAllUseCase
from authkit.usecases.Authentication.logout_all_with_otp_start import StartLogoutAllWithOTPUseCase
from authkit.usecases.Authentication.logout_all_with_otp_verify import VerifyLogoutAllWithOTPUseCase
from authkit.usecases.Authentication.registration import RegistrationUseCase
from authkit.usecases.Authentication.registration_with_otp_start import StartRegistrationWithOTPUseCase            
from authkit.usecases.Authentication.registration_with_otp_verify import VerifyRegistrationWithOTPUseCase

__all__ = [
    "LoginUseCase",
    "StartLoginWithOTPUseCase",
    "VerifyLoginWithOTPUseCase",
    "LogoutUseCase",
    "LogoutAllUseCase",
    "StartLogoutAllWithOTPUseCase",
    "VerifyLogoutAllWithOTPUseCase",
    "RegistrationUseCase",
    "StartRegistrationWithOTPUseCase",
    "VerifyRegistrationWithOTPUseCase",
]