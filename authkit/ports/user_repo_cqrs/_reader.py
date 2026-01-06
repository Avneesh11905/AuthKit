from typing import Protocol
from uuid import UUID
from authkit.domain import User

class UserReaderRepository(Protocol):
    """
    Interface for user data persistence.
    """
    def get_by_identifier(self, identifier: str) -> User | None:
        """
        Retrieves a user by their identifier (e.g., email or username).

        Args:
            identifier: The user's unique identifier.

        Returns:
            The User object if found, None otherwise.
        """
        ...

    def get_by_id(self, user_id: UUID) -> User | None:
        """
        Retrieves a user by their unique ID.

        Args:
            user_id: The user's UUID.

        Returns:
            The User object if found, None otherwise.
        """
        ...