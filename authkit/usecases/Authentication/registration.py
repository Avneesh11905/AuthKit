from authkit.ports.user_repo_cqrs import UserWriterRepository
from authkit.ports.passwd_manager import PasswordManager
from authkit.domain import User
from uuid import uuid4

class RegistrationUseCase:
    """
    Use case for registering a new user locally.
    """
    def __init__(self , user_writer: UserWriterRepository , password_store: PasswordManager):
        self.user_writer = user_writer
        self.password_store = password_store
    
    async def execute(self, identifier: str, password: str):
        """
        Registers a new user with an identifier and password.
        
        Args:
            identifier: The user's public identifier (e.g., email).
            password: The validation password.
            
        Returns:
            The newly created User object.
        """
        hashed_password = await self.password_store.hash(password)
        user = User(id=uuid4(),identifier=identifier, password_hash=hashed_password , credentials_version=0)
        user_added = await self.user_writer.add(user)
        return user_added