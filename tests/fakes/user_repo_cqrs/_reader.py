from tests.fakes.user_repo_cqrs.user_store import FakeUserStore, fake_to_user
from authkit.domain import User
from uuid import UUID

class FakeUserReaderRepository:
    """
    Fake implementation of UserReaderRepository.
    """
    def __init__(self, store: FakeUserStore):
        self.store = store

    def get_by_identifier(self, identifier: str) -> User | None:
        """
        Retrieves a user by identifier if not deleted.
        """
        for fake_user in self.store.users.values():
            if fake_user.identifier == identifier:
                if fake_user.deleted:
                    return None
                return fake_to_user(fake_user)    
        return None
    
    def get_by_id(self, user_id: UUID) -> User | None:
        """
        Retrieves a user by ID if not deleted.
        """
        fake_user = self.store.users.get(user_id)
        if fake_user is None or fake_user.deleted:
            return None
        return fake_to_user(fake_user)

    def get_all(self):
        return [fake_to_user(fake_user) for fake_user in self.store.users.values()]