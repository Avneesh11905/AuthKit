import bcrypt , asyncio

class FakePasswordManager:
    """
    Fake implementation of PasswordManager for testing purposes.
    Uses bcrypt for realistic hashing but runs in-memory.
    """
    async def hash(self, password: str) -> str:
        """
        Hashes a password using bcrypt.
        """
        hashed = await asyncio.to_thread(
            bcrypt.hashpw,
            password.encode(),
            bcrypt.gensalt(12)
        )
        return hashed.decode()
    
    async def verify(self, password: str, hashed_password: str) -> bool:
        """
        Verifies a password against a bcrypt hash.
        """
        result = await asyncio.to_thread(
            bcrypt.checkpw,
            password.encode(),
            hashed_password.encode()
        )
        return result