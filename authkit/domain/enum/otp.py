from enum import Enum

class OTPPurpose(Enum):
    """
    Enumeration of valid purposes for generating an OTP.
    """
    REGISTRATION = "registration"
    FORGET_PASSWORD = "forget_password"
    MFA = "mfa"
