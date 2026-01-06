import secrets
from uuid import UUID, uuid4
from datetime import datetime

# 1. CORE IMPORTS
from authkit import AuthKit, User
from authkit.exceptions import ConflictError
from authkit.ports import Session
from dataclasses import dataclass

@dataclass
class QuickStartSession:
    token: str
    session_id: UUID
    credentials_version: int
    revoked: bool = False

# 2. DEFINE SIMPLE ADAPTERS (Normally these would be database/service integrations)
# For this example, we use simple in-memory dictionaries.

class InMemoryUserRepo:
    """Combines UserReader and UserWriter for simplicity."""
    def __init__(self):
        self.users: dict[UUID, User] = {}

    def get_by_identifier(self, identifier: str) -> User | None:
        for u in self.users.values():
            if u.identifier == identifier:
                return u
        return None
    
    def get_by_id(self, user_id: UUID) -> User | None:
        return self.users.get(user_id)
        
    def add(self, user: User) -> User:
        if self.get_by_identifier(user.identifier):
            raise ConflictError("User exists")
        self.users[user.id] = user
        return user
        
    def update_last_login(self, user_id: UUID) -> None:
        if user_id in self.users:
            self.users[user_id].last_login = datetime.now()

    def delete(self, user_id: UUID) -> None:
        self.users.pop(user_id, None)

class SimplePasswordManager:
    """Uses a simple reversal for demonstration (DO NOT USE IN PRODUCTION)."""
    def hash(self, password: str) -> str:
        return "hashed_" + password[::-1]
    
    def verify(self, password: str, hashed_password: str) -> bool:
        return hashed_password == "hashed_" + password[::-1]

class InMemorySessionService:
    """Simple random token generator."""
    def issue(self, user_id: UUID, credential_version: int) -> QuickStartSession:
        return QuickStartSession(
            token=secrets.token_urlsafe(32),
            session_id=uuid4(),
            credentials_version=credential_version
        )
        
    def verify(self, token: str, creds_version: int) -> bool:
        return True
        
    def revoke(self, user_id: UUID, session_id: UUID) -> bool:
        return True
        
    def revoke_all(self, user_id: UUID) -> None:
        pass

# --- OTP & Intent Adapters (For MFA Demos) ---
class InMemoryOTPStore:
    def __init__(self): self.codes = {}
    def store(self, token, code, purpose): self.codes[token] = code
    def get(self, token, purpose): return self.codes.get(token)
    def verify(self, token, purpose, code): return self.codes.get(token) == code

class InMemoryOTPManager:
    def generate(self): return "123456" # Fixed for demo
    def send(self, identifier, code, purpose): print(f"   [OTP SENT] To: {identifier}, Code: {code}")

class FakeIntentStore:
    def __init__(self): self.store_db = {}
    def store(self, intent): 
        token = uuid4()
        self.store_db[token] = intent
        return token
    def get(self, key): return self.store_db.get(key)
    def delete(self, key): self.store_db.pop(key, None)

# 3. RUN THE APPLICATION
def main():
    print("--- AuthKit Quick Start (with Facade) ---\n")
    
    # Direct Initialization: No need to import Factory or Adapters!
    auth = AuthKit(
        user_repo=InMemoryUserRepo(),
        password_manager=SimplePasswordManager(),
        session_service=InMemorySessionService()
    )
    
    email = "newuser@example.com"
    password = "MySecurePassword123!"
    
    try:
        # 1. Register
        print(f"-> Registering user: {email}")
        user = auth.register.execute(email, password)
        print(f"   Success! User ID: {user.id}")
        
        # 2. Login
        print(f"\n-> Logging in...")
        auth_token = auth.login.execute(email, password)
        print(f"   Success! Access Token: {auth_token.token}")
        
        # 3. Configure OTP (Simulating runtime upgrade or explicit init)
        print(f"\n-> Configuring OTP features...")
        auth.configure(
            otp_store=InMemoryOTPStore(),
            otp_manager=InMemoryOTPManager(),
            intent_store=FakeIntentStore()
        )
        
        # 4. Delete Account with OTP
        print(f"\n-> Deleting account (Secure Flow)...")
        # Start
        verify_token = auth.delete_account_otp_start.execute(user.id)
        print(f"   Started! Verification Token: {verify_token}")
        
        # Verify (Simulate user entering "123456")
        deleted_id = auth.delete_account_otp_verify.execute(verify_token, "123456")
        print(f"   Success! Account deleted for User ID: {deleted_id}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
