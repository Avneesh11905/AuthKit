from typing import Protocol

class PasswordManager(Protocol):
    """
    Interface for hashing and verifying passwords.
    """
    def hash(self, password: str) -> str: 
        """
        Hashes a plain text password.
        
        Args:
            password: The plain text password to hash.
            
        Returns:
            The hashed password string.
        """
        ...

    def verify(self, password: str, hashed_password: str) -> bool: 
        """
        Verifies a plain text password against a hash.
        
        Args:
            password: The plain text password.
            hashed_password: The hashed password to verify against.
            
        Returns:
            True if the password matches the hash, False otherwise.
        """
        ...