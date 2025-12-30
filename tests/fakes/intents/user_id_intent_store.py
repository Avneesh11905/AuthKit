from uuid import UUID , uuid4

class FakeUserIDIntentStore:
    """
    Fake implementation of UserIDIntentStore using in-memory dictionary.

    """
    def __init__(self):
        self.intents: dict[UUID, UUID] = {}

    async def store(self, intent: UUID) -> UUID: 
        """
        Stores a user ID intent.
        """
        key = uuid4()
        self.intents[key] = intent
        return key

    async def get(self, key: UUID) -> UUID | None: 
        """
        Retrieves a user ID intent.
        """
        return self.intents.get(key)

    async def delete(self, key: UUID) -> None: 
        """
        Deletes a user ID intent.
        """
        del self.intents[key]

