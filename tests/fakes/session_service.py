import secrets
from uuid import UUID , uuid4
from dataclasses import dataclass, field

@dataclass
class FakeSession:
    token: str
    credentials_version: int 
    session_id: UUID = field(default_factory=uuid4)
    revoked: bool = False 

class FakeSessionService:
    """
    Fake implementation of SessionService using in-memory dictionary.
    """
    def __init__(self):
        self.sessions: dict[str, FakeSession] = {}

    def issue(self, user_id: UUID, credential_version: int) -> FakeSession:
        """
        Issues a new fake session.
        """
        sess_str = secrets.token_urlsafe(32)
        fake_session = FakeSession(token=sess_str,
                                credentials_version=credential_version)
        self.sessions[f'{user_id}:{fake_session.session_id}'] = fake_session
        return fake_session
    
    def verify(self, token: str , creds_version: int) -> bool: 
        """
        Verifies if a session exists, is not revoked, and matches credential version.
        """
        for stored in self.sessions.values():
            if stored.token == token:
                if stored.revoked:
                    return False
                if stored.credentials_version != creds_version:
                    return False
                return True
        return False
       
    def revoke(self, user_id: UUID, session_id: UUID) -> bool:
        """
        Revokes a specific session by marking it as revoked.
        """
        key = f'{user_id}:{session_id}'
        sess = self.sessions.get(key)
        if sess is None:
            return False
        self.sessions[key].revoked = True
        return True

    def revoke_all(self, user_id: UUID):
        """
        Revokes all sessions for a given user.
        """
        for k in list(self.sessions.keys()):
            if k.startswith(f'{user_id}:'):
                self.sessions[k].revoked = True
