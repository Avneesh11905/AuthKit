from authkit.ports.user_repo import UserRepository 
from authkit.ports.passwd_manager import PasswordManager
from authkit.ports.token_service import TokenService , Token
from authkit.exceptions.auth import InvalidCredentialsError

class LoginUseCase:
    """
    Use case for authenticating a user with credentials.
    """
    def __init__(self,
                 user_repo: UserRepository,
                 password_manager: PasswordManager,
                 token_service: TokenService,
                 ):

        self.user_repo = user_repo
        self.password_manager = password_manager
        self.token_service = token_service

    async def execute(self, identifier: str, password: str ) -> Token:
        """
        Authenticates a user and issues a token.
        
        Args:
            identifier: The user's identifier (email/username).
            password: The user's password.
            
        Returns:
            A Token object representing the authenticated session.
            
        Raises:
            InvalidCredentialsError: If the user is not found or password is incorrect.
        """
        user = await self.user_repo.get_by_identifier(identifier)
        if not user:
            raise InvalidCredentialsError("User not found")
        valid = await self.password_manager.verify(password, user.password_hash)
        if not valid:
            raise InvalidCredentialsError("Invalid password")
        token = await self.token_service.issue(user.id, user.credentials_version)
        await self.user_repo.update_last_login(user.id)
        return token