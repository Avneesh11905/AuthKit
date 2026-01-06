import pytest
from uuid import UUID, uuid4
from dataclasses import dataclass
# Ideally we would import these from the library, but for valid tests we import from source
from authkit import AuthKit, User
from authkit.exceptions import ConflictError
from authkit.ports import AuthSession
from authkit.domain import OTPPurpose

# --- FAKES for Testing ---

@dataclass
class QuickStartSession:
    token: str
    session_id: UUID
    credentials_version: int
    revoked: bool = False

class InMemoryUserRepo:
    def __init__(self): 
        self.users: dict[UUID, User] = {}
    
    def get_by_identifier(self, identifier: str) -> User | None:
        for u in self.users.values():
            if u.identifier == identifier: return u
        return None
    
    def get_by_id(self, user_id: UUID) -> User | None: 
        return self.users.get(user_id)
    
    def add(self, user: User) -> User:
        if self.get_by_identifier(user.identifier): 
            raise ConflictError("User exists")
        self.users[user.id] = user
        return user
    
    def update_last_login(self, user_id: UUID) -> None: pass
    def delete(self, user_id: UUID) -> None: self.users.pop(user_id, None)

class SimplePasswordManager:
    def hash(self, password: str) -> str: return "hashed_" + password
    def verify(self, password: str, hashed_password: str) -> bool: 
        return hashed_password == "hashed_" + password

class InMemoryAuthSessionService:
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

# --- FIXTURES ---

@pytest.fixture
def auth():
    return AuthKit(
        user_repo=InMemoryUserRepo(),
        password_manager=SimplePasswordManager(),
        session_service=InMemoryAuthSessionService(),
        otp_store=InMemoryOTPStore(),
        otp_manager=InMemoryOTPManager(),
        registration_intent_store=FakeIntentStore()
    )

# --- TESTS ---

def test_register_with_metadata(auth):
    """Test standard registration with metadata."""
    meta = {"fullname": "Test User", "age": 25}
    user = auth.register.execute("test@example.com", "pass", metadata=meta)
    
    assert user is not None
    assert user.metadata == meta
    assert user.metadata["fullname"] == "Test User"

def test_register_without_metadata(auth):
    """Test registration defaults to empty metadata."""
    user = auth.register.execute("empty@example.com", "pass")
    assert user.metadata == {}

def test_otp_registration_flow_with_metadata(auth):
    """Test metadata persistence through OTP registration flow."""
    otp_meta = {"role": "moderator", "verified": False}
    identifier = "otp@example.com"
    
    # 1. Start
    token = auth.register_otp_start.execute(identifier, "pass", metadata=otp_meta)
    
    # 2. Verify
    # Code is fixed fake "123456"
    user = auth.register_otp_verify.execute(token, "123456")
    
    assert user.identifier == identifier
    assert user.metadata == otp_meta
    assert user.metadata["role"] == "moderator"

def test_metadata_isolation(auth):
    """Ensure metadata objects are independent (not shared instances)."""
    user1 = auth.register.execute("u1@example.com", "pass", metadata={"a": 1})
    user2 = auth.register.execute("u2@example.com", "pass", metadata={"b": 2})
    
    user1.metadata["a"] = 999
    assert user2.metadata["b"] == 2
    assert "a" not in user2.metadata
