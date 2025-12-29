import secrets
from uuid import UUID , uuid4
from pydantic import BaseModel , Field

class FakeToken(BaseModel):
    token: str
    token_id: UUID = Field(default_factory=uuid4)
    revoked: bool = Field(default=False)
    credentials_version: int 

class FakeTokenService:
    def __init__(self):
        self.tokens: dict[str, FakeToken] = {}

    async def issue(self, user_id: UUID, credential_version: int) -> FakeToken:
        token = secrets.token_urlsafe(32)
        fake_token = FakeToken(token=token,
                                credentials_version=credential_version)
        self.tokens[f'{user_id}:{fake_token.token_id}'] = fake_token
        return fake_token
    
    async def verify(self, token: str , creds_version: int) -> bool: 
        for stored in self.tokens.values():
            if stored.token == token:
                if stored.revoked:
                    return False
                if stored.credentials_version != creds_version:
                    return False
                return True
        return False
       
    async def revoke(self, user_id: UUID, token_id: UUID) -> bool:
        key = f'{user_id}:{token_id}'
        token = self.tokens.get(key)
        if token is None:
            return False
        self.tokens[key].revoked = True
        return True

    async def revoke_all(self, user_id: UUID):
        prefix = f'{user_id}:'
        for k in list(self.tokens.keys()):
            if k.startswith(prefix):
                self.tokens[k].revoked = True
