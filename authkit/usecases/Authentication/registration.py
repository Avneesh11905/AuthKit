from authkit.ports.user_repo_cqrs import UserWriterRepository
from authkit.ports.passwd_manager import PasswordManager
from authkit.domain import User
from uuid import uuid4
from typing import Any

from authkit.core import Registry

@Registry.register("register")
class RegistrationUseCase:
    """
    Use case for registering a new user locally.
    """
    def __init__(self , user_writer: UserWriterRepository , password_manager: PasswordManager):
        self.user_writer = user_writer
        self.password_manager = password_manager
    
    def execute(self, identifier: str, password: str, metadata: dict[str, Any] | None = None):
        """
        Registers a new user with an identifier and password.
        
        Args:
            identifier: The user's public identifier (e.g., email).
            password: The validation password.
            metadata: Optional dictionary for additional user data.
            
        Returns:
            The newly created User object.
        """
        hashed_password = self.password_manager.hash(password)
        user = User(
            id=uuid4(),
            identifier=identifier, 
            password_hash=hashed_password, 
            credentials_version=0,
            metadata=metadata or {}
        )
        user_added = self.user_writer.add(user)
        return user_added