# Demonstrates Unit of Work (transactional) consistency with AuthKit
from dataclasses import dataclass
from authkit import AuthKit, User
from authkit.ports import UserRepository, AuthSessionService, AuthSession
from authkit.exceptions import ConflictError
from uuid import UUID

# --- Mock SQLAlchemy Session ---
class MockSession:
    def commit(self): print("  [DB] COMMIT transaction")
    def rollback(self): print("  [DB] ROLLBACK transaction")
    def close(self): print("  [DB] CLOSE connection")
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type:
                self.rollback()
                print(f"  [UOW] Error detected: {exc_val}. Rolled back.")
            else:
                self.commit()
                print("  [UOW] Success. Committed.")
        finally:
            self.close()

# --- Mock Repository ---
@dataclass
class SqlAlchemyUserRepo(UserRepository):
    session: MockSession
    def get_by_identifier(self, identifier): 
        # Stub: Return a fake user if email matches
        if identifier == "user@example.com":
            from authkit.domain import User
            from uuid import uuid4
            return User(id=uuid4(), identifier=identifier, password_hash="hashed_password", credentials_version=0)
        return None
        
    def get_by_id(self, user_id):
        # Stub for verifying credentials version
        from authkit.domain import User
        return User(id=user_id, identifier="user@example.com", password_hash="hashed_password", credentials_version=0)
        
    def update_last_login(self, user_id):
        pass # No-op

# --- The Unit of Work Pattern ---
# --- Generic Unit of Work (Purely for DB) ---
class GenericUnitOfWork:
    def __init__(self, session: MockSession):
        self.session = session

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type:
                self.session.rollback()
                print(f"  [UOW] Error detected: {exc_val}. Rolled back.")
            else:
                self.session.commit()
                print("  [UOW] Success. Committed.")
        finally:
            self.session.close()

# --- Usage Example ---

def run_example():
    # 1. Setup (App Startup)
    class StubPasswordManager:
        def verify(self, p, h): return True
        def hash(self, p): return "hashed"
        
    class StubAuthSessionService:
        def issue(self, user_id: UUID, credential_version: int) -> AuthSession:
            from uuid import uuid4
            
            @dataclass
            class MockAuthSession:
                token: str
                session_id: UUID
                credentials_version: int
                revoked: bool = False
                
            return MockAuthSession(token="mock_token", session_id=uuid4(), credentials_version=credential_version)
        def verify(self, t, c): return True
        def revoke(self, u, s): pass
        def revoke_all(self, u): pass
        
    # Create a Global AuthKit instance (Singleton-ish)
    auth = AuthKit(
        password_manager=StubPasswordManager(),
        session_service=StubAuthSessionService()
    )
    
    # 2. Execution (Per Request)
    print("--- Request 1: Decoupled UOW + AuthKit ---")
    
    # You have your generic DB UOW...
    session = MockSession()
    with GenericUnitOfWork(session=session) as session:
        # Inside the business logic, you CONFIGURE the existing AuthKit instance
        print("  [Logic] Configuring AuthKit for this context...")
        auth.configure(user_repo=SqlAlchemyUserRepo(session=session))
        
        # Now use AuthKit
        auth.login.execute("user@example.com", "password")

    print("\n--- Request 2: Direct Session Usage (What you asked for) ---")
    # This simulates "with Session() as session:"
    with MockSession() as session:
        print("  [Logic] Re-configuring AuthKit for this session...")
        # Inject the repository bound to THIS session
        auth.configure(user_repo=SqlAlchemyUserRepo(session))
        
        # Now use it!
        auth.login.execute("user@example.com", "password")
         
if __name__ == "__main__":
    run_example()
