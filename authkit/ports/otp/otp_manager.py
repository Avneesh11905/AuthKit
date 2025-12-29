from typing import Protocol
from authkit.domain import OTPPurpose

class OTPManager(Protocol):
    """
    Interface for generating and sending OTPs (One-Time Passwords).
    """

    async def generate(self) -> str: 
        """
        Generates a new OTP code.
        
        Returns:
            The generated OTP string.
        """
        ...

    async def send(self, identifier: str, code: str, purpose: OTPPurpose) -> None: 
        """
        Sends an OTP to a user.
        
        For Example: Via Email or SMS
        
        Args:
            identifier: The destination (e.g., email or phone number).
            code: The OTP code to send.
            purpose: The purpose of the OTP (e.g., login, registration).
        """
        ...
