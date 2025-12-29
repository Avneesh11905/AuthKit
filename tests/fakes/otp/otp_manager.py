from authkit import OTPPurpose
import string , secrets

class FakeOTPManager:
    async def generate(self) -> str: 
        return ''.join(secrets.choice(string.digits) for i in range(6))

    async def send(self, identifier: str, code: str, purpose: OTPPurpose) -> None: 
        pass