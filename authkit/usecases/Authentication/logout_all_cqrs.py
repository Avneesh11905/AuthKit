from authkit.ports.token_service import TokenService
from authkit.ports.user_repo_cqrs import UserWriterRepository , UserReaderRepository
from authkit.exceptions.auth import NotFoundError
from uuid import UUID

class LogoutAllCQRSUseCase:
    """
    Use case for logging out a user from all sessions using CQRS pattern.
    """
    def __init__(self, 
                 user_writer: UserWriterRepository,
                 user_reader: UserReaderRepository,
                 token_service: TokenService ):
        self.user_writer = user_writer
        self.user_reader = user_reader
        self.token_service = token_service

    async def execute(self , user_id: UUID):
        """
        Revokes all tokens for a user and increments their credential version.
        
        Args:
            user_id: The ID of the user.
            
        Raises:
            NotFoundError: If the user does not exist.
        """
        user = await self.user_reader.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        await self.token_service.revoke_all(user_id)

        await self.user_writer.increment_credentials_version(user_id)