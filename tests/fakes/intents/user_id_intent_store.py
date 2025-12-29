from uuid import UUID , uuid4

class FakeUserIDIntentStore:
    """
        Suggestion : save the otp using key like intent:registration:{intent.id}
    """
    def __init__(self):
        self.intents: dict[UUID, UUID] = {}

    async def store(self, intent: UUID) -> UUID: 
        key = uuid4()
        self.intents[key] = intent
        return key

    async def get(self, key: UUID) -> UUID | None: 
        return self.intents.get(key)

    async def delete(self, key: UUID) -> None: 
        del self.intents[key]

