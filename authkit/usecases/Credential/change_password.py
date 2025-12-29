from authkit.ports.passwd_manager import PasswordManager
from authkit.ports.user_repo import UserRepository
from authkit.ports.token_service import TokenService
from authkit.exceptions import NotFoundError , InvalidCredentialsError
from uuid import UUID

class ChangePasswordUseCase:
    """
    Use case for changing a user's password.
    """
    def __init__(self,
                 user_repo: UserRepository,
                 password_manager: PasswordManager,
                 token_service: TokenService):
        self.user_repo = user_repo
        self.password_manager = password_manager
        self.token_service = token_service
    
    async def execute(self, user_id: UUID, old_password: str, new_password: str) -> None:
        """
        Changes the user's password.
        
        Verifies the old password, revokes all existing tokens, increments the 
        credential version, and updates the password hash.
        
        Args:
            user_id: The ID of the user.
            old_password: The current password.
            new_password: The new password.
            
        Raises:
            InvalidCredentialsError: If possible password reuse or invalid old password.
            NotFoundError: If user not found.
        """
        if old_password == new_password:
            raise InvalidCredentialsError("New password must be different")
        user = await self.user_repo.get_by_id(user_id=user_id)
        if not user:
            raise NotFoundError("User not found")
        if not await self.password_manager.verify(password=old_password, hashed_password=user.password_hash):
            raise InvalidCredentialsError("Invalid password")
        await self.token_service.revoke_all(user_id=user_id)
        await self.user_repo.increment_credentials_version(user_id=user_id)
        hashed_password = await self.password_manager.hash(password=new_password)
        await self.user_repo.change_password(user_id=user_id, new_password_hash=hashed_password)
