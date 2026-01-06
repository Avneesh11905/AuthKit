from typing import Protocol
from uuid import UUID

class AuthSession(Protocol):
    """
    Represents an issued authentication session.
    
    Attributes:
        session_id (UUID): Unique identifier for this specific session (JTI).
        token (str): The actual encoded token string (e.g., JWT).
        credentials_version (int): The version of credentials this session is tied to.
        revoked (bool): Whether this session has been explicitly revoked.
    """
    token: str
    session_id: UUID
    credentials_version: int
    revoked: bool = False

class AuthSessionService(Protocol):
    """
    Interface for Token Management (Issuance, Verification, Revocation).
    
    This port handles the lifecycle of authentication tokens. Implementations can be
    stateful (database-backed tokens) or stateless (JWTs), though `revoke_all`
    usually requires some state mechanism (like blacklisting or versioning).
    """

    def issue(self, user_id: UUID, credential_version: int) -> AuthSession: 
        """
        Generates and issues a new authentication token for a user.
        
        Args:
            user_id (UUID): The unique ID of the user.
            credential_version (int): The current security version of the user's credentials.
                                      Used to invalidate old tokens when passwords change.
            
        Returns:
            AuthSession: A simplified object containing the token string and ID.
        """
        ...
        
    def verify(self, token: str, creds_version: int) -> bool: 
        """
        Validates an incoming token string.
        
        Verification must check:
        1. Signature validity.
        2. Expiration time.
        3. Credential Version matching (session version == user version).
        
        Args:
            token (str): The raw token string to verify.
            creds_version (int): The current credential version from the User entity.
            
        Returns:
            bool: True if valid, False if expired, tampered, or obsolete.
        """
        ...
        
    def revoke(self, user_id: UUID, session_id: UUID) -> bool: 
        """
        Revokes a single specific session.
        
        Args:
            user_id (UUID): The owner of the session.
            session_id (UUID): The unique ID of the session to revoke.
            
        Returns:
            bool: True if successfully revoked.
        """
        ...
        
    def revoke_all(self, user_id: UUID) -> None: 
        """
        Global Logout: Revokes ALL tokens for a given user.
        
        This is typically achieved by incrementing the user's `credential_version`
        in the User Repository, rendering all previous tokens invalid during `verify()`.
        
        Args:
            user_id (UUID): The user to globally log out.
        """
        ...