from authkit.ports.user_repo_cqrs import UserReaderRepository , UserWriterRepository
from authkit.ports.passwd_manager import PasswordManager
from authkit.ports.token_service import TokenService , Token
from authkit.exceptions.auth import InvalidCredentialsError

class LoginCQRSUseCase:
    """
    Use case for authenticating a user with credentials using CQRS pattern.
    """
    def __init__(self,
                 user_reader: UserReaderRepository,
                 user_writer: UserWriterRepository,
                 password_manager: PasswordManager,
                 token_service: TokenService,
                 ):

        self.user_reader = user_reader
        self.password_manager = password_manager
        self.token_service = token_service
        self.user_writer = user_writer

    async def execute(self, identifier: str, password: str ) -> Token:
        """
        Authenticates a user and issues a token using CQRS repositories.
        
        Args:
            identifier: The user's identifier (email/username).
            password: The user's password.
            
        Returns:
            A Token object representing the authenticated session.
            
        Raises:
            InvalidCredentialsError: If the user is not found or password is incorrect.
        """
        user = await self.user_reader.get_by_identifier(identifier)
        if not user:
            raise InvalidCredentialsError("User not found")
        valid = await self.password_manager.verify(password, user.password_hash)
        if not valid:
            raise InvalidCredentialsError("Invalid password")
        token = await self.token_service.issue(user.id, user.credentials_version)
        await self.user_writer.update_last_login(user.id)
        return token