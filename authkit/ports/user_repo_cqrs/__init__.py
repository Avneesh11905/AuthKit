"""
Exposes the CQRS-style user repository interfaces.
"""
from authkit.ports.user_repo_cqrs._reader import UserReaderRepository
from authkit.ports.user_repo_cqrs._writer import UserWriterRepository

__all__ = [
    "UserReaderRepository",
    "UserWriterRepository",
]