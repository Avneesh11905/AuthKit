from dataclasses import dataclass
from uuid import UUID

@dataclass
class RegistrationIntent:
    """
    Data required for registering a new user, held temporarily during the OTP flow.
    """
    identifier: str
    password_hash: str
    credentials_version: int
