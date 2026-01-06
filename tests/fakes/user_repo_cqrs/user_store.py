from uuid import UUID
from authkit.domain import User
from dataclasses import dataclass , field
from datetime import datetime


@dataclass
class FakeUser:
    id: UUID
    identifier : str
    password_hash : str
    credentials_version : int 
    deleted : bool = field(default=False)
    last_login : datetime | None = field(default=None)

def user_to_fake(user: User) -> FakeUser:
    return FakeUser(id=user.id,
                    identifier=user.identifier,
                    password_hash=user.password_hash,
                    credentials_version=user.credentials_version,
                    last_login=user.last_login)

def fake_to_user(fake: FakeUser) -> User:
    return User(id=fake.id, 
                identifier=fake.identifier, 
                password_hash=fake.password_hash, 
                credentials_version=fake.credentials_version,
                last_login=fake.last_login)

class FakeUserStore:
    """
    Singleton holder for the in-memory user storage.
    """
    def __init__(self):
        self.users: dict[UUID, FakeUser] = {}

fake_user_store = FakeUserStore()
