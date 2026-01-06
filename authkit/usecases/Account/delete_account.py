from authkit.ports.session_service import SessionService
from authkit.ports.user_repo_cqrs import UserReaderRepository , UserWriterRepository
from uuid import UUID

from authkit.core import Registry

@Registry.register("delete_account")
class DeleteAccountUseCase:
    """
    Use case for deleting a user account using CQRS pattern.
    """
    def __init__(self, 
                 user_reader: UserReaderRepository,
                 user_writer: UserWriterRepository,
                session_service: SessionService ):
        self.user_reader = user_reader
        self.user_writer = user_writer
        self.session_service = session_service

    def execute(self, user_id: UUID) -> UUID:
        """
        Deletes the user account and revokes all associated tokens.
        
        Args:
            user_id: The ID of the user to delete.
            
        Returns:
            The ID of the deleted user.
        """
        user = self.user_reader.get_by_id(user_id)
        if user is None:
            return user_id
        self.session_service.revoke_all(user_id)
        self.user_writer.delete(user_id)
        return user_id
        