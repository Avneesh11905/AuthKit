from uuid import UUID, uuid4
from authkit import AuthKit, User 
from authkit.exceptions import ConflictError
from authkit.ports import Session
from dataclasses import dataclass
from typing import Any

# --- MOCKS ---

@dataclass
class QuickStartSession:
    token: str
    session_id: UUID
    credentials_version: int
    revoked: bool = False

class InMemoryUserRepo:
    def __init__(self): self.users: dict[UUID, User] = {}
    def get_by_identifier(self, identifier: str) -> User | None:
        for u in self.users.values():
            if u.identifier == identifier: return u
        return None
    def get_by_id(self, user_id: UUID) -> User | None: return self.users.get(user_id)
    def add(self, user: User) -> User:
        if self.get_by_identifier(user.identifier): raise ConflictError("User exists")
        self.users[user.id] = user
        return user
    def update_last_login(self, user_id: UUID) -> None: pass
    def delete(self, user_id: UUID) -> None: self.users.pop(user_id, None)

class SimplePasswordManager:
    def hash(self, password: str) -> str: return "hashed_" + password
    def verify(self, password: str, hashed_password: str) -> bool: return hashed_password == "hashed_" + password

class InMemorySessionService:
    def issue(self, user_id: UUID, credential_version: int) -> QuickStartSession:
        return QuickStartSession(token="tok", session_id=uuid4(), credentials_version=credential_version)
    def verify(self, token: str, creds_version: int) -> bool: return True
    def revoke(self, user_id: UUID, session_id: UUID) -> bool: return True
    def revoke_all(self, user_id: UUID) -> None: pass

class InMemoryOTPStore:
    def __init__(self): self.codes = {}
    def store(self, token, code, purpose): self.codes[token] = code
    def get(self, token, purpose): return self.codes.get(token)
    def verify(self, token, purpose, code): return self.codes.get(token) == code

class InMemoryOTPManager:
    def generate(self): return "123456"
    def send(self, identifier, code, purpose): pass

class FakeIntentStore:
    def __init__(self): self.store_db = {}
    def store(self, intent): 
        token = uuid4()
        self.store_db[token] = intent
        return token
    def get(self, key): return self.store_db.get(key)
    def delete(self, key): self.store_db.pop(key, None)

# --- TESTS ---

def test_metadata():
    print("Testing Metadata Support...")
    
    auth = AuthKit(
        user_repo=InMemoryUserRepo(),
        password_manager=SimplePasswordManager(),
        session_service=InMemorySessionService(),
        otp_store=InMemoryOTPStore(),
        otp_manager=InMemoryOTPManager(),
        registration_intent_store=FakeIntentStore()
    )
    
    # 1. Standard Registration with Metadata
    meta = {"fullname": "John Doe", "role": "admin", "age": 30}
    print(f"1. Registering with metadata: {meta}")
    user = auth.register.execute("john@example.com", "pass", metadata=meta)
    
    assert user.metadata == meta
    assert user.metadata['fullname'] == "John Doe"
    print("   [PASS] User created with correct metadata.")
    
    # 2. Default (Empty) Metadata
    print("2. Registering without metadata (should be empty dict)")
    user2 = auth.register.execute("jane@example.com", "pass")
    assert user2.metadata == {}
    print("   [PASS] User created with empty metadata.")

    # 3. OTP Registration Flow with Metadata
    print("3. Testing OTP Registration with Metadata")
    otp_meta = {"fullname": "OTP User"}
    
    # Start
    token = auth.register_otp_start.execute("otp@example.com", "pass", metadata=otp_meta)
    print(f"   started, token: {token}")
    
    # Verify
    user3 = auth.register_otp_verify.execute(token, "123456")
    assert user3.metadata == otp_meta
    assert user3.metadata['fullname'] == "OTP User"
    print("   [PASS] OTP User created with correct metadata.")
    
    print("\nALL TESTS PASSED!")

if __name__ == "__main__":
    test_metadata()
