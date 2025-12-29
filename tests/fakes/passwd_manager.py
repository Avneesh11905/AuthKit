import bcrypt , asyncio

class FakePasswordManager:
    async def hash(self, password: str) -> str:
        hashed = await asyncio.to_thread(
            bcrypt.hashpw,
            password.encode(),
            bcrypt.gensalt(12)
        )
        return hashed.decode()
    
    async def verify(self, password: str, hashed_password: str) -> bool:
        result = await asyncio.to_thread(
            bcrypt.checkpw,
            password.encode(),
            hashed_password.encode()
        )
        return result