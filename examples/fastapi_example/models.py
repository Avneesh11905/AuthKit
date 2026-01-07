from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel
from datetime import datetime

# --- Database Models ---

class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    identifier: str = Field(index=True, unique=True)
    password_hash: str
    credentials_version: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    deleted: bool = Field(default=False)
    last_login: datetime | None = Field(default=None)

class UserSession(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True) # session_id
    user_id: UUID = Field(index=True)
    refresh_token: str = Field(index=True) # The actual refresh token string
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    revoked: bool = Field(default=False)

# ... (Previous Request Models)

class MFAVerifyRequest(SQLModel):
    token: UUID
    otp: str
    
    # Metadata stored as JSON string (simplified for demo) if needed, 
    # or just additional columns. For strict AuthKit compat, we map this.

# --- Pydantic Schemas for API ---

class RegisterRequest(SQLModel):
    email: str
    password: str

class RegisterStartRequest(SQLModel):
    email: str
    password: str

class RegisterVerifyRequest(SQLModel):
    token: UUID
    otp: str
class LoginRequest(SQLModel):
    email: str
    password: str
class RefreshTokenRequest(SQLModel):
    refresh_token: str

class RecoverStartRequest(SQLModel):
    email: str

class RecoverVerifyRequest(SQLModel):
    token: UUID
    otp: str
    new_password: str

class UserResponse(SQLModel):
    id: UUID
    email: str
    active: bool
