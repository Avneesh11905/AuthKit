from authkit.ports.user_repo_cqrs import UserReaderRepository , UserWriterRepository
from authkit.ports.passwd_manager import PasswordManager 
from authkit.ports.session_service import AuthSessionService , AuthSession
from authkit.exceptions import InvalidCredentialsError

from authkit.core import Registry

@Registry.register("login")
class LoginUseCase:
    """
    Use case for authenticating a user with credentials using CQRS pattern.
    """
    def __init__(self,
                 user_reader: UserReaderRepository,
                 user_writer: UserWriterRepository,
                 password_manager: PasswordManager,
                 session_service: AuthSessionService,
                 ):

        self.user_reader = user_reader
        self.password_manager = password_manager
        self.session_service = session_service
        self.user_writer = user_writer

    def execute(self, identifier: str, password: str ) -> AuthSession:
        """
        Authenticates a user and issues a token using CQRS repositories.
        
        Args:
            identifier: The user's identifier (email/username).
            password: The user's password.
            
        Returns:
            A AuthSession object representing the authenticated session.
            
        Raises:
            InvalidCredentialsError: If the user is not found or password is incorrect.
        """
        user = self.user_reader.get_by_identifier(identifier)
        if not user:
            raise InvalidCredentialsError("User not found")
        valid = self.password_manager.verify(password, user.password_hash)
        if not valid:
            raise InvalidCredentialsError("Invalid password")
        token = self.session_service.issue(user_id=user.id, creds_version=user.credentials_version)
        self.user_writer.update_last_login(user_id=user.id)
        return token