from authkit.ports.token_service import TokenService
from authkit.ports.user_repo_cqrs import UserReaderRepository , UserWriterRepository
from uuid import UUID

class DeleteAccountCQRSUseCase:
    """
    Use case for deleting a user account using CQRS pattern.
    """
    def __init__(self, 
                 user_reader: UserReaderRepository,
                 user_writer: UserWriterRepository,
                 token_service: TokenService ):
        self.user_reader = user_reader
        self.user_writer = user_writer
        self.token_service = token_service

    async def execute(self, user_id: UUID) -> UUID:
        """
        Deletes the user account and revokes all associated tokens.
        
        Args:
            user_id: The ID of the user to delete.
            
        Returns:
            The ID of the deleted user.
        """
        user = await self.user_reader.get_by_id(user_id)
        if user is None:
            return user_id
        await self.token_service.revoke_all(user_id)
        await self.user_writer.delete(user_id)
        return user_id
        