from authkit.ports.session_service import AuthSessionService
from uuid import UUID
from authkit.exceptions.auth import NotFoundError

from authkit.core import Registry

@Registry.register("logout")
class LogoutUseCase:
    """
    Use case for logging out a user (revoking a single token).
    """
    def __init__(self, session_service: AuthSessionService):
        self.session_service = session_service
    
    def execute(self, user_id: UUID, token_id: UUID):
        """
        Revokes a specific session token.
        
        Args:
            user_id: The ID of the user.
            token_id: The ID of the token to revoke.
            
        Raises:
            NotFoundError: If the token is invalid or does not belong to the user.
        """
        revoked = self.session_service.revoke(user_id, token_id)
        if not revoked:
            raise NotFoundError("Token not found or not owned by user")