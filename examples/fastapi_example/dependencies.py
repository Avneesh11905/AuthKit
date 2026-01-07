from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
from authkit import AuthKit 
from authkit.core.adapters import AuthAdapters

from .database import get_session, redis_client
from .adapters import (
    SQLModelUserRepository, 
    RedisAuthSessionService, 
    RedisOTPStore, 
    RedisRegistrationIntentStore,
    RedisUserIDIntentStore,
    ConsoleOTPManager
)
from .models import User
from sqlmodel import Session , select

# --- Authorization Scheme ---
# Using HTTPBearer allows "Paste Token" in Swagger, needed for complex MFA flows
security_scheme = HTTPBearer()

# --- Dependency Injection for AuthKit ---
def get_authkit(session: Session = Depends(get_session)) -> AuthKit:
    # 1. Initialize Adapters
    user_repo = SQLModelUserRepository(session)
    session_service = RedisAuthSessionService(redis_client, session)
    
    # Simple password manager (using library or custom implementation)
    # Ideally use passlib or bcrypt. For demo, we do a very naive "hash" (don't do this in prod!)
    class SimplePasswordManager():
        def hash(self, password: str) -> str:
            return f"hashed_{password}"
        def verify(self, password: str, hashed_password: str) -> bool:
            return f"hashed_{password}" == hashed_password
            
    password_manager = SimplePasswordManager()
    
    otp_store = RedisOTPStore(redis_client)
    otp_manager = ConsoleOTPManager()
    reg_intent = RedisRegistrationIntentStore(redis_client)
    user_intent = RedisUserIDIntentStore(redis_client)

    adapters = AuthAdapters(
        session_service=session_service,
        password_manager=password_manager,
        user_repo=user_repo,
        otp_store=otp_store,
        otp_manager=otp_manager,
        registration_intent_store=reg_intent,
        intent_store=user_intent
    )

    # 2. Return initialized Facade
    return AuthKit(adapters=adapters)

# --- Dependency: Get Current User ---
import jwt
from .adapters import SECRET_KEY, ALGORITHM
def get_current_user(
    auth_creds: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
    auth: Annotated[AuthKit, Depends(get_authkit)],
    session: Session = Depends(get_session)
):
    token = auth_creds.credentials
    try:
        # 1. Decode JWT (without signature verification first to get ID, or with if we have Key)
        # We share SECRET_KEY here so we can fully decode.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        if not user_id:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        from uuid import UUID
        # 2. Get User
        user = auth._adapters.user_repo.get_by_id(UUID(user_id))
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
            
        # 3. Verify Token (Signature + Credential Version + Revocation Check)
        # The session_service 'verify' now handles looking up Redis for revocation
        # Use _adapters because AuthKit stores it privately
        is_valid = auth._adapters.session_service.verify(token, user.credentials_version)
        if not is_valid:
             raise HTTPException(status_code=401, detail="Session expired or invalid")
             
        return user
        
    except jwt.PyJWTError as e:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        # Catch-all
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

