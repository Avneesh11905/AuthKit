from authkit.ports.session_service import SessionService
from authkit.ports.user_repo_cqrs import UserWriterRepository , UserReaderRepository
from authkit.exceptions.auth import NotFoundError
from uuid import UUID

from authkit.core import Registry

@Registry.register("logout_all")
class LogoutAllUseCase:
    """
    Use case for logging out a user from all sessions using CQRS pattern.
    """
    def __init__(self, 
                 user_writer: UserWriterRepository,
                 user_reader: UserReaderRepository,
                 session_service: SessionService ):
        self.user_writer = user_writer
        self.user_reader = user_reader
        self.session_service = session_service

    def execute(self , user_id: UUID):
        """
        Revokes all tokens for a user and increments their credential version.
        
        Args:
            user_id: The ID of the user.
            
        Raises:
            NotFoundError: If the user does not exist.
        """
        user = self.user_reader.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        self.session_service.revoke_all(user_id)

        self.user_writer.increment_credentials_version(user_id)