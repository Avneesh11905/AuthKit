from uuid import UUID
from authkit.domain import User
from tests.fakes.user_repo_cqrs.user_store import FakeUserStore, user_to_fake
from authkit.exceptions import UserNotFoundError , ConflictError
from datetime import datetime


class FakeUserWriterRepository:
    """
    Fake implementation of UserWriterRepository.
    """
    def __init__(self, store: FakeUserStore):
        self.store = store

    async def add(self, user: User) -> User:
        """
        Adds a new user.
        Raises ConflictError if user already exists.
        """
        for fake_user in self.store.users.values():
            if fake_user.identifier == user.identifier:
                if fake_user.deleted:
                    break
                raise ConflictError("User already exists")
        
        fake_user = user_to_fake(user)
        self.store.users[fake_user.id] = fake_user
        return user

    async def update_last_login(self, user_id: UUID) -> None:
        """
        Updates the last_login timestamp.
        """
        fake_user = self.store.users.get(user_id)
        if fake_user is None or fake_user.deleted:
            raise UserNotFoundError("User not found") 
        self.store.users[user_id].last_login = datetime.now()

    async def delete(self, user_id: UUID) -> None:
        """
        Soft-deletes a user.
        """
        fake_user = self.store.users.get(user_id)
        if fake_user is None :
            raise UserNotFoundError("User not found")
        self.store.users[user_id].deleted = True
    
    async def increment_credentials_version(self, user_id: UUID) -> None:
        """
        Increments the user's credentials version.
        """
        fake_user = self.store.users.get(user_id)
        if fake_user is None or fake_user.deleted:
            raise UserNotFoundError("User not found")
        self.store.users[user_id].credentials_version += 1

    async def change_password(self, user_id: UUID, new_password_hash: str) -> None:
        """
        Updates the user's password hash.
        """
        fake_user = self.store.users.get(user_id)
        if fake_user is None or fake_user.deleted:
            raise UserNotFoundError("User not found")
        self.store.users[user_id].password_hash = new_password_hash