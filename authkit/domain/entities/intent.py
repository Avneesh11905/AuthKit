from dataclasses import dataclass, field
from uuid import UUID
from typing import Any

@dataclass
class RegistrationIntent:
    """
    Data required for registering a new user, held temporarily during the OTP flow.
    """
    identifier: str
    password_hash: str
    credentials_version: int
    metadata: dict[str, Any] = field(default_factory=dict)