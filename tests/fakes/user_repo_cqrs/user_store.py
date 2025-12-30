from uuid import UUID
from authkit.domain import User
from pydantic import BaseModel, Field
from datetime import datetime

class FakeUser(BaseModel):
    id: UUID
    identifier : str
    password_hash : str
    credentials_version : int 
    deleted : bool = Field(default=False)
    last_login : datetime | None = Field(default=None)

def user_to_fake(user: User) -> FakeUser:
    return FakeUser(**user.__dict__)

def fake_to_user(fake: FakeUser) -> User:
    return User(id=fake.id, 
                identifier=fake.identifier, 
                password_hash=fake.password_hash, 
                credentials_version=fake.credentials_version)

class FakeUserStore:
    """
    Singleton holder for the in-memory user storage.
    """
    def __init__(self):
        self.users: dict[UUID, FakeUser] = {}

fake_user_store = FakeUserStore()
