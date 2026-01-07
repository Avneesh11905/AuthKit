from typing import Any, Optional
from uuid import UUID, uuid4
import json
from sqlmodel import Session, select
import redis
from datetime import timedelta

from authkit.ports import (
    UserReaderRepository, 
    UserWriterRepository, 
    AuthSessionService, 
    AuthSession, 
    OTPStore, 
    OTPManager
)
from authkit import User as DomainUser, RegistrationIntent, OTPPurpose ,RegistrationIntentStore , UserIDIntentStore
from .models import User as DBUser, UserSession as DBUserSession

# --- User Repository ---
class SQLModelUserRepository(UserReaderRepository, UserWriterRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_identifier(self, identifier: str) -> Optional[DomainUser]:
        statement = select(DBUser).where(DBUser.identifier == identifier)
        results = self.session.exec(statement)
        db_user = results.first()
        if db_user:
            return self._to_domain(db_user)
        return None

    def get_by_id(self, user_id: UUID) -> Optional[DomainUser]:
        db_user = self.session.get(DBUser, user_id)
        if db_user:
            return self._to_domain(db_user)
        return None

    def add(self, user: DomainUser) -> DomainUser:
        db_user = DBUser(
            id=user.id,
            identifier=user.identifier,
            password_hash=user.password_hash,
            credentials_version=user.credentials_version,
            is_active=True
        )
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return self._to_domain(db_user)

    def update(self, user: DomainUser) -> DomainUser:
        db_user = self.session.get(DBUser, user.id)
        if db_user:
            db_user.identifier = user.identifier
            db_user.password_hash = user.password_hash
            db_user.credentials_version = user.credentials_version
            self.session.add(db_user)
            self.session.commit()
            self.session.refresh(db_user)
            return self._to_domain(db_user)
        return user # Should actully raise not found, but tailored for example

    def delete(self, user: DomainUser) -> None:
        db_user = self.session.get(DBUser, user.id)
        if db_user:
            self.session.delete(db_user)
            self.session.commit()

    def update_last_login(self, user_id: UUID) -> None:
        db_user = self.session.get(DBUser, user_id)
        if db_user:
            db_user.last_login = datetime.utcnow()
            self.session.add(db_user)
            self.session.commit()

    def _to_domain(self, db_user: DBUser) -> DomainUser:
        return DomainUser(
            id=db_user.id,
            identifier=db_user.identifier,
            password_hash=db_user.password_hash,
            credentials_version=db_user.credentials_version
        )

# --- Redis Session Service (JWT Access + Opaque Refresh) ---
import jwt
from datetime import datetime

SECRET_KEY = "super-secret-key-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

class RedisAuthSessionService(AuthSessionService):
    def __init__(self, redis: redis.Redis, db_session: Session):
        self.redis = redis
        self.db_session = db_session

    def issue(self, user_id: UUID, credential_version: int) -> AuthSession:
        return self._create_session(user_id, credential_version)
        
    def _create_session(self, user_id: UUID, credential_version: int, existing_session_id: UUID = None) -> AuthSession:
        session_id = existing_session_id or uuid4()
        
        # Refresh Token = "user_id:session_id" so we can lookup the key later
        refresh_token = f"{user_id}:{session_id}"
        
        # 1. Create Access Token (JWT) - Short Lived
        now = datetime.utcnow()
        access_expires = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        access_payload = {
            "sub": str(user_id),
            "jti": str(session_id),
            "ver": credential_version,
            "exp": access_expires,
            "iat": now,
            "type": "access"
        }
        access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)
        
        # 2. Store Session in Redis
        # Key Pattern: session:{user_id}:{session_id}
        key = f"session:{user_id}:{session_id}"
        
        refresh_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        data = {
            "user_id": str(user_id),
            "cred_ver": credential_version,
            "active": "1"
        }
        self.redis.hset(key, mapping=data)
        self.redis.expire(key, refresh_expires)
        
        # 3. Store Session in SQL (Persistence)
        # Check if already exists (for sliding window updates, though usually we create new if rotation)
        # If refreshing involves creating new session ID, this is always new.
        # If we reuse session ID, we might need to update expiration.
        # Current logic: _create_session called by refresh() which reuses ID.
        
        db_session_entry = self.db_session.get(DBUserSession, session_id)
        if not db_session_entry:
            db_session_entry = DBUserSession(
                id=session_id,
                user_id=user_id,
                refresh_token=refresh_token,
                expires_at=now + refresh_expires
            )
            self.db_session.add(db_session_entry)
        else:
            # Update expiry for sliding window
            db_session_entry.expires_at = now + refresh_expires
            self.db_session.add(db_session_entry)
            
        self.db_session.commit()

        class TokenPairSession:
            def __init__(self, access, refresh, sid, cver):
                self.token = access 
                self.refresh_token = refresh 
                self.session_id = sid
                self.credentials_version = cver
                self.revoked = False

        return TokenPairSession(access_token, refresh_token, session_id, credential_version)

    def refresh(self, refresh_token: str) -> Optional[AuthSession]:
        try:
            # Parse composite token
            user_id_str, session_id_str = refresh_token.split(":")
            user_id = UUID(user_id_str)
            session_id = UUID(session_id_str)
        except ValueError:
            return None

        key = f"session:{user_id}:{session_id}"
        if not self.redis.exists(key):
            return None
            
        data = self.redis.hgetall(key)
        cred_ver = int(data["cred_ver"])
        
        # Reuse session ID (Slide window)
        return self._create_session(user_id, cred_ver, existing_session_id=session_id)

    def verify(self, token: str, creds_version: int) -> bool:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            if payload.get("type") != "access":
                return False
                
            session_id = payload.get("jti")
            user_id = payload.get("sub") # JWT has 'sub'
            token_ver = payload.get("ver")
            
            if not session_id or not user_id or token_ver is None:
                return False
            
            if int(token_ver) != creds_version:
                return False

            # Check Redis using new key pattern
            key = f"session:{user_id}:{session_id}"
            if not self.redis.exists(key):
                return False
                
            return True
        except jwt.PyJWTError:
            return False

    def revoke(self, user_id: UUID, session_id: UUID) -> bool:
        # Revoke in Redis
        key = f"session:{user_id}:{session_id}"
        redis_revoked = bool(self.redis.delete(key))
        
        # Revoke in SQL
        db_session = self.db_session.get(DBUserSession, session_id)
        if db_session:
            db_session.revoked = True
            self.db_session.add(db_session)
            self.db_session.commit()
            return True
        
        return redis_revoked

    def revoke_all(self, user_id: UUID) -> None:
        # Pattern match all sessions for this user in Redis
        pattern = f"session:{user_id}:*"
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)
            
        # SQL: Mark all active sessions for user as revoked
        statement = select(DBUserSession).where(DBUserSession.user_id == user_id, DBUserSession.revoked == False)
        sessions = self.db_session.exec(statement).all()
        for s in sessions:
            s.revoked = True
            self.db_session.add(s)
        self.db_session.commit()

# --- Redis OTP Store ---
class RedisOTPStore(OTPStore):
    def __init__(self, redis: redis.Redis, ttl_seconds: int = 300):
        self.redis = redis
        self.ttl = ttl_seconds

    def _key(self, token: UUID, purpose: OTPPurpose) -> str:
        return f"otp:{purpose.value}:{token}"

    def store(self, token: UUID, code: str, purpose: OTPPurpose) -> None:
        key = self._key(token, purpose)
        self.redis.set(key, code, ex=self.ttl)

    def verify(self, token: UUID, code: str, purpose: OTPPurpose) -> bool:
        key = self._key(token, purpose)
        stored_code = self.redis.get(key)
        # Note: In real world, invalidate OTP after use (delete it)
        # Here we just check comparison
        if stored_code == code:
            self.redis.delete(key) # Prevent replay
            return True
        return False

# --- Redis Intent Stores ---
class RedisRegistrationIntentStore(RegistrationIntentStore):
    def __init__(self, redis: redis.Redis, ttl_seconds: int = 600):
        self.redis = redis
        self.ttl = ttl_seconds

    def store(self, intent: RegistrationIntent) -> UUID:
        token = uuid4()
        key = f"reg_intent:{token}"
        # Serialize intent
        data = {
            "identifier": intent.identifier,
            "password_hash": intent.password_hash,
            "credentials_version": intent.credentials_version,
            "metadata": json.dumps(intent.metadata)
        }
        self.redis.hset(key, mapping=data)
        self.redis.expire(key, self.ttl)
        return token

    def get(self, key: UUID) -> Optional[RegistrationIntent]:
        redis_key = f"reg_intent:{key}"
        if not self.redis.exists(redis_key):
            return None
        data = self.redis.hgetall(redis_key)
        return RegistrationIntent(
            identifier=data["identifier"],
            password_hash=data["password_hash"],
            credentials_version=int(data["credentials_version"]),
            metadata=json.loads(data["metadata"])
        )

    def delete(self, key: UUID) -> None:
        redis_key = f"reg_intent:{key}"
        self.redis.delete(redis_key)

class RedisUserIDIntentStore(UserIDIntentStore):
    def __init__(self, redis: redis.Redis, ttl_seconds: int = 600):
        self.redis = redis
        self.ttl = ttl_seconds

    def store(self, intent: UUID) -> UUID:
        token = uuid4() # The public token
        key = f"user_intent:{token}"
        self.redis.set(key, str(intent), ex=self.ttl)
        return token

    def get(self, key: UUID) -> Optional[UUID]:
        redis_key = f"user_intent:{key}"
        user_id_str = self.redis.get(redis_key)
        if user_id_str:
            return UUID(user_id_str)
        return None

    def delete(self, key: UUID) -> None:
        redis_key = f"user_intent:{key}"
        self.redis.delete(redis_key)


# --- Console OTP Manager ---
from random import randint

class ConsoleOTPManager(OTPManager):
    def generate(self) -> str:
        return str(randint(100000, 999999))

    def send(self, identifier: str, code: str, user_reader: Any, purpose: OTPPurpose) -> None:
        print(f"========================================")
        print(f"OTP SENT TO {identifier} for {purpose.value}")
        print(f"CODE: {code}")
        print(f"========================================")
