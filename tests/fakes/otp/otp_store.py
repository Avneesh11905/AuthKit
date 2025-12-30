from uuid import UUID
from authkit import OTPPurpose

class FakeOTPStore:
    """
    Fake implementation of OTPStore using in-memory dictionary.
    """
    def __init__(self):
        self.codes: dict[str, str] = {}

    async def store(self, token: UUID, code: str, purpose: OTPPurpose) -> None:
        """
        Stores an OTP mapped to a token and purpose.
        """
        self.codes[f'{token}:{purpose}'] = code
    
    async def verify(self, token: UUID, code: str, purpose: OTPPurpose) -> bool: 
        """
        Verifies and consumes the OTP.
        """
        saved = self.codes.get(f'{token}:{purpose}')
        if saved is None:
            return False
        validity = (code == saved)
        del self.codes[f'{token}:{purpose}']
        return validity

    async def get(self, token: UUID, purpose: OTPPurpose) -> str | None:
        """
        Retrieves the stored OTP (helper for testing).
        """
        return self.codes.get(f'{token}:{purpose}')
    
    def __repr__(self):
        print(self.codes)