from authkit.ports.passwd_manager import PasswordManager
from authkit.ports.user_repo_cqrs import UserReaderRepository , UserWriterRepository
from authkit.ports.session_service import AuthSessionService
from authkit.exceptions import NotFoundError , InvalidCredentialsError
from uuid import UUID

from authkit.core import Registry

@Registry.register("change_password")
class ChangePasswordUseCase:
    """
    Use case for changing a user's password using CQRS pattern.
    """
    def __init__(self,
                 user_reader: UserReaderRepository,
                 user_writer: UserWriterRepository,
                 password_manager: PasswordManager,
                 session_service: AuthSessionService):
        self.user_reader = user_reader
        self.user_writer = user_writer
        self.password_manager = password_manager
        self.session_service = session_service
    
    def execute(self, user_id: UUID, old_password: str, new_password: str) -> None:
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
        user = self.user_reader.get_by_id(user_id=user_id)
        if not user:
            raise NotFoundError("User not found")
        if not self.password_manager.verify(password=old_password, hashed_password=user.password_hash):
            raise InvalidCredentialsError("Invalid password")
        self.session_service.revoke_all(user_id=user_id)
        self.user_writer.increment_credentials_version(user_id=user_id)
        hashed_password = self.password_manager.hash(password=new_password)
        self.user_writer.change_password(user_id=user_id, new_password_hash=hashed_password)
