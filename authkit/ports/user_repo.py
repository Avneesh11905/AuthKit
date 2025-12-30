from authkit.ports.user_repo_cqrs import UserReaderRepository, UserWriterRepository
from typing import Protocol

class UserRepository(UserReaderRepository, UserWriterRepository, Protocol):
    """
    Composite interface combining both read and write operations for users.
    Useful for storage implementations that support both (e.g., SQL databases).
    """
    ...