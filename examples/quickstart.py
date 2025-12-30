import asyncio
import secrets
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field

# 1. CORE IMPORTS
from authkit import RegistrationUseCase, LoginCQRSUseCase
from authkit.domain import User
from authkit.exceptions import UserNotFoundError, ConflictError
from authkit.ports import PasswordManager

# 2. DEFINE SIMPLE ADAPTERS (Normally these would be database/service integrations)
# For this example, we use simple in-memory dictionaries.

class InMemoryUserRepo:
    """Combines UserReader and UserWriter for simplicity."""
    def __init__(self):
        self.users: dict[UUID, User] = {}

    async def get_by_identifier(self, identifier: str) -> User | None:
        for u in self.users.values():
            if u.identifier == identifier:
                return u
        return None
    
    async def get(self, user_id: UUID) -> User | None:
        return self.users.get(user_id)
        
    async def add(self, user: User) -> User:
        if await self.get_by_identifier(user.identifier):
            raise ConflictError("User exists")
        self.users[user.id] = user
        return user
        
    async def update_last_login(self, user_id: UUID) -> None:
        if user_id in self.users:
            self.users[user_id].last_login = datetime.now()

class SimplePasswordManager:
    """Uses a simple reversal for demonstration (DO NOT USE IN PRODUCTION)."""
    async def hash(self, password: str) -> str:
        return "hashed_" + password[::-1]
    
    async def verify(self, password: str, hashed_password: str) -> bool:
        return hashed_password == "hashed_" + password[::-1]

class InMemoryToken:
    """Token DTO"""
    def __init__(self, token: str, token_id: UUID):
        self.token = token
        self.token_id = token_id

class InMemoryTokenService:
    """Simple random token generator."""
    async def issue(self, user_id: UUID, credential_version: int) -> InMemoryToken:
        return InMemoryToken(
            token=secrets.token_urlsafe(32),
            token_id=uuid4()
        )

# 3. RUN THE APPLICATION
async def main():
    print("--- AuthKit Quick Start ---\n")
    
    # A. Setup Dependencies
    user_repo = InMemoryUserRepo()
    password_manager = SimplePasswordManager()
    token_service = InMemoryTokenService()
    
    # B. Initialize Use Cases
    # Inject dependencies into the Use Cases
    register_uc = RegistrationUseCase(user_repo, password_manager)
    login_uc = LoginCQRSUseCase(user_repo, user_repo, password_manager, token_service)
    
    # C. Execute Flows
    email = "newuser@example.com"
    password = "MySecurePassword123!"
    
    try:
        # 1. Register
        print(f"-> Registering user: {email}")
        user = await register_uc.execute(email, password)
        print(f"   Success! User ID: {user.id}")
        
        # 2. Login
        print(f"\n-> Logging in...")
        auth_token = await login_uc.execute(email, password)
        print(f"   Success! Access Token: {auth_token.token}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
