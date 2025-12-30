from typing import Protocol
from uuid import UUID
from authkit.domain import User

class UserWriterRepository(Protocol):
    async def add(self, user: User) -> User:
        """
        Persists a new user.

        Args:
            user: The User object to add.

        Returns:
            The added User object.
        """
        ...

    async def update_last_login(self, user_id: UUID) -> None:
        """
        Updates the last login timestamp for a user.

        Args:
            user_id: The ID of the user.
        """
        ...

    async def delete(self, user_id: UUID) -> None:
        """
        Deletes (or soft-deletes) a user.

        Args:
            user_id: The ID of the user to delete.
        """
        ...

    async def increment_credentials_version(self, user_id: UUID) -> None:
        """
        Increments the user's credential version, invalidating existing tokens.

        Args:
            user_id: The ID of the user.
        """
        ...

    async def change_password(self, user_id: UUID, new_password_hash: str) -> None:
        """
        Updates the user's password hash.

        Args:
            user_id: The ID of the user.
            new_password_hash: The new hashed password.
        """
        ...