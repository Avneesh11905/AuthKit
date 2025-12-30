from uuid import UUID , uuid4
from authkit import RegistrationIntent

class FakeRegistrationIntentStore:
    """
    Fake implementation of RegistrationIntentStore using in-memory dictionary.
    """
    def __init__(self):
        self.intent_store: dict[UUID, RegistrationIntent] = {}

    async def store(self, intent: RegistrationIntent) -> UUID: 
        """
        Stores a registration intent.
        """
        key = uuid4()
        self.intent_store[key] = intent
        return key
    
    async def get(self, key: UUID) -> RegistrationIntent | None: 
        """
        Retrieves a registration intent.
        """
        return self.intent_store.get(key)

    async def delete(self, key: UUID) -> None: 
        """
        Deletes a registration intent.
        """
        check = self.intent_store.get(key)
        if check is None:
            return 
        del self.intent_store[key]


