from typing import Protocol
from uuid import UUID

class Token(Protocol):
    token_id: UUID
    token: str
    revoked: bool

class TokenService(Protocol):
    """
    Interface for managing authentication tokens.
    """
    async def issue(self, user_id: UUID, credential_version: int) -> Token: 
        """
        Issues a new token for a user.
        
        Args:
            user_id: The ID of the user.
            credential_version: The current credential version of the user.
            
        Returns:
            A Token object containing the token string and metadata.
        """
        ...
        
    async def verify(self, token: str , creds_version: int) -> bool: 
        """
        Verifies if a token is valid and not revoked.
        
        Args:
            token: The token string to verify.
            creds_version: The user's current credential version.
            
        Returns:
            True if the token is valid, False otherwise.
        """
        ...
        
    async def revoke(self, user_id: UUID, token_id: UUID) -> bool: 
        """
        Revokes a specific token.
        
        Args:
            user_id: The ID of the user owning the token.
            token_id: The unique identifier of the token.
            
        Returns:
            True if the token was successfully revoked.
        """
        ...
        
    async def revoke_all(self , user_id: UUID) -> None: 
        """
        Revokes all tokens for a specific user.
        
        Args:
            user_id: The ID of the user.
        """
        ...