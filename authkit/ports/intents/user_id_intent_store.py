from typing import Protocol
from uuid import UUID

class UserIDIntentStore(Protocol):
    """
    Interface for storing temporary intents mapped to User IDs.
    Suggestion: save the otp using key like intent:{intent.id}
    """
    def store(self, intent: UUID) -> UUID: 
        """
        Stores a user ID as an intent.
        
        Args:
            intent: The User ID to store.
            
        Returns:
            A new unique key (UUID) for accessing this intent.
        """
        ...
        
    def get(self, key: UUID) -> UUID | None: 
        """
        Retrieves a user ID by its intent key.
        
        Args:
            key: The intent key.
            
        Returns:
            The User ID if found, None otherwise.
        """
        ...
        
    def delete(self, key: UUID) -> None: 
        """
        Deletes an intent.
        
        Args:
            key: The intent key to delete.
        """
        ...

