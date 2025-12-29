from uuid import UUID
from authkit import OTPPurpose

class FakeOTPStore:
    def __init__(self):
        self.codes: dict[str, str] = {}

    async def store(self, token: UUID, code: str, purpose: OTPPurpose) -> None:
        self.codes[f'{token}:{purpose}'] = code
    
    async def verify(self, token: UUID, code: str, purpose: OTPPurpose) -> bool: 
        saved = self.codes.get(f'{token}:{purpose}')
        if saved is None:
            return False
        validity = (code == saved)
        del self.codes[f'{token}:{purpose}']
        return validity

    async def get(self, token: UUID, purpose: OTPPurpose) -> str | None:
        return self.codes.get(f'{token}:{purpose}')
    
    def __repr__(self):
        print(self.codes)