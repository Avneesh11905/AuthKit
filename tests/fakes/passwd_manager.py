import bcrypt 

class FakePasswordManager:
    """
    Fake implementation of PasswordManager for testing purposes.
    Uses bcrypt for realistic hashing but runs in-memory.
    """
    def hash(self, password: str) -> str:
        """
        Hashes a password using bcrypt.
        """
        return bcrypt.hashpw(password.encode(),bcrypt.gensalt(12)).decode()
    
    def verify(self, password: str, hashed_password: str) -> bool:
        """
        Verifies a password against a bcrypt hash.
        """
        return bcrypt.checkpw(password.encode(),hashed_password.encode())