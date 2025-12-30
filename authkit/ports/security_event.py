from uuid import UUID
from typing import Protocol

class SecurityEventPublisher(Protocol):
    """
    Interface for publishing security-related events.
    """

    async def login_success(self, user_id: UUID): 
        """
        Publishes a login success event.
        
        Args:
            user_id: The ID of the logged-in user.
        """
        ...

    async def login_failure(self, identifier: str): 
        """
        Publishes a login failure event.
        
        Args:
            identifier: The identifier used in the failed attempt.
        """
        ...

    async def otp_failed(self, user_id: UUID): 
        """
        Publishes an OTP verification failure event.
        
        Args:
            user_id: The ID of the user.
        """
        ...

    async def account_locked(self, user_id: UUID): 
        """
        Publishes an account locked event.
        
        Args:
            user_id: The ID of the user whose account was locked.
        """
        ...