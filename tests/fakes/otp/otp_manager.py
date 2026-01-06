from authkit import OTPPurpose
import string , secrets

class FakeOTPManager:
    """
    Fake implementation of OTPManager. Generates random digits and provides a stub for sending.
    """
    def generate(self) -> str: 
        """
        Generates a 6-digit random OTP.
        """
        return ''.join(secrets.choice(string.digits) for i in range(6))

    def send(self, identifier: str, code: str, purpose: OTPPurpose) -> None: 
        """
        Stub for sending the OTP (does nothing).
        """
        pass