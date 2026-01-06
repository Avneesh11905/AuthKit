from uuid import UUID
from typing import Protocol
from authkit.domain import OTPPurpose

class OTPStore(Protocol):
    """
    Interface for storing and verifying OTPs.
    Suggestion: save the otp using key like otp:{purpose}:{token} -> hashed(otp)
    """
    def store(self, token: UUID, code: str, purpose: OTPPurpose) -> None: 
        """
        Stores an OTP for verification.
        
        Args:
            token: The verification token associated with the OTP.
            code: The OTP code.
            purpose: The purpose of the OTP.
        """
        ...

    def verify(self, token: UUID, code: str, purpose: OTPPurpose) -> bool: 
        """
        Verifies an OTP against the stored value.
        
        Args:
            token: The verification token.
            code: The OTP code to verify.
            purpose: The purpose of the OTP.
            
        Returns:
            True if the OTP is valid, False otherwise.
        """
        ...
