from uuid import UUID , uuid4
from authkit import RegistrationIntent

class FakeRegistrationIntentStore:
    """
        Suggestion : save the otp using key like intent:registration:{intent.id}
    """
    def __init__(self):
        self.intent_store: dict[UUID, RegistrationIntent] = {}

    async def store(self, intent: RegistrationIntent) -> UUID: 
        key = uuid4()
        self.intent_store[key] = intent
        return key
    
    async def get(self, key: UUID) -> RegistrationIntent | None: 
        return self.intent_store.get(key)

    async def delete(self, key: UUID) -> None: 
        check = self.intent_store.get(key)
        if check is None:
            return 
        del self.intent_store[key]


