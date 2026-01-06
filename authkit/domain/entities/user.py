from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
@dataclass
class User:
    """
    Represents a user in the system.
    
    Attributes:
        id: Unique identifier for the user.
        identifier: Public identifier (e.g., email).
        password_hash: Hashed password string.
        credentials_version: Version number for invalidating tokens on credential changes.
    """
    id: UUID
    identifier: str
    password_hash: str
    credentials_version: int
    last_login: datetime | None = None
