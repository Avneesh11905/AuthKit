from authkit.ports.token_service import TokenService
from authkit.ports.user_repo import UserRepository
from uuid import UUID

class DeleteAccountUseCase:
    """
    Use case for deleting a user account.
    """
    def __init__(self, 
                 user_repo: UserRepository,
                 token_service: TokenService ):
        self.user_repo = user_repo
        self.token_service = token_service

    async def execute(self, user_id: UUID) -> UUID:
        """
        Deletes the user account and revokes all associated tokens.
        
        Args:
            user_id: The ID of the user to delete.
            
        Returns:
            The ID of the deleted user.
        """
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            return user_id
        await self.token_service.revoke_all(user_id)
        await self.user_repo.delete(user_id)
        return user_id
        