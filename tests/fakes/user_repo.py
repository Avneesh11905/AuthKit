from uuid import UUID
from authkit import User 
from pydantic import BaseModel , Field
from datetime import datetime
from authkit.exceptions import UserNotFoundError , ConflictError

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

class FakeUserRepository:
    """
    Fake implementation of UserRepository using an in-memory dictionary.
    """
    def __init__(self):
        self.fake_user_store: dict[UUID, FakeUser] = {}

    async def get_by_identifier(self, identifier: str) -> User | None:
        """
        Retrieves a user by identifier if not deleted.
        """
        for fake_user in self.fake_user_store.values():
            if fake_user.identifier == identifier:
                if fake_user.deleted:
                    return None
                return fake_to_user(fake_user)    
        return None
    
    async def get_by_id(self, user_id: UUID) -> User | None:
        """
        Retrieves a user by ID if not deleted.
        """
        fake_user = self.fake_user_store.get(user_id)
        if fake_user is None or fake_user.deleted:
            return None
        return fake_to_user(fake_user)

    async def add(self, user: User) -> User:
        """
        Adds a new user to the store.
        Raises ConflictError if user already exists.
        """
        for fake_user in self.fake_user_store.values():
            if fake_user.identifier == user.identifier:
                if fake_user.deleted:
                    break
                raise ConflictError("User already exists")
        fake_user = user_to_fake(user)
        self.fake_user_store[fake_user.id] = fake_user
        return user

    async def update_last_login(self, user_id: UUID) -> None:
        """
        Updates the last_login timestamp.
        """
        fake_user = self.fake_user_store.get(user_id)
        if fake_user is None or fake_user.deleted:
            raise UserNotFoundError("User not found") 
        self.fake_user_store[user_id].last_login = datetime.now()

    async def delete(self, user_id: UUID) -> None:
        """
        Soft-deletes a user.
        """
        fake_user = self.fake_user_store.get(user_id)
        if fake_user is None :
            raise UserNotFoundError("User not found")
        self.fake_user_store[user_id].deleted = True
    
    async def increment_credentials_version(self, user_id: UUID) -> None:
        """
        Increments the user's credentials version.
        """
        fake_user = self.fake_user_store.get(user_id)
        if fake_user is None or fake_user.deleted:
            raise UserNotFoundError("User not found")
        self.fake_user_store[user_id].credentials_version += 1

    async def change_password(self, user_id: UUID, new_password_hash: str) -> None:
        """
        Updates the user's password hash.
        """
        fake_user = self.fake_user_store.get(user_id)
        if fake_user is None or fake_user.deleted:
            raise UserNotFoundError("User not found")
        self.fake_user_store[user_id].password_hash = new_password_hash
