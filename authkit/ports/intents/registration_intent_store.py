from typing import Protocol
from uuid import UUID
from authkit.domain import RegistrationIntent

class RegistrationIntentStore(Protocol):
    """
    Interface for storing temporary registration data.
    Suggestion: save the otp using key like intent:registration:{intent.id}
    """
    async def store(self, intent: RegistrationIntent) -> UUID: 
        """
        Stores registration intent data.
        
        Args:
            intent: The RegistrationIntent object.
            
        Returns:
            A new unique key (UUID) for accessing this intent.
        """
        ...
        
    async def get(self, key: UUID) -> RegistrationIntent | None: 
        """
        Retrieves registration intent data.
        
        Args:
            key: The intent key.
            
        Returns:
            The RegistrationIntent object if found, None otherwise.
        """
        ...
        
    async def delete(self, key: UUID) -> None: 
        """
        Deletes a registration intent.
        
        Args:
            key: The intent key to delete.
        """
        ...

