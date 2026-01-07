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
    
    def execute(self, user_id: UUID, session_id: UUID):
        """
        Revokes a specific session token.
        
        Args:
            user_id: The ID of the user.
            session_id: The ID of the session to revoke.
            
        Raises:
            NotFoundError: If the session is invalid or does not belong to the user.
        """
        revoked = self.session_service.revoke(user_id, session_id)
        if not revoked:
            raise NotFoundError("Session not found or not owned by user")