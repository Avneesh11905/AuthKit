from authkit.ports.token_service import TokenService
from uuid import UUID
from authkit.exceptions.auth import NotFoundError

class LogoutUseCase:
    """
    Use case for logging out a user (revoking a single token).
    """
    def __init__(self, token_service: TokenService):
        self.token_service = token_service
    
    async def execute(self, user_id: UUID, token_id: UUID):
        """
        Revokes a specific session token.
        
        Args:
            user_id: The ID of the user.
            token_id: The ID of the token to revoke.
            
        Raises:
            NotFoundError: If the token is invalid or does not belong to the user.
        """
        revoked = await self.token_service.revoke(user_id, token_id)
        if not revoked:
            raise NotFoundError("Token not found or not owned by user")