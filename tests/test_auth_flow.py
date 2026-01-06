import pytest
import secrets
from tests.auth import auth
from authkit.exceptions import InvalidCredentialsError ,ConflictError

def test_registration_success():
    email = f"user_{secrets.token_hex(4)}@example.com"
    password = "secure_password"
    
    user = auth.register.execute(email, password)
    
    assert user.identifier == email
    assert user.id is not None

def test_registration_duplicate_fail():
    email = f"user_{secrets.token_hex(4)}@example.com"
    password = "secure_password"
    
    auth.register.execute(email, password)
    
    with pytest.raises(ConflictError):
        auth.register.execute(email, password)

def test_login_success():
    email = f"user_{secrets.token_hex(4)}@example.com"
    password = "secure_password"
    
    user = auth.register.execute(email, password)
    
    session = auth.login.execute(email, password)
    
    assert session.token is not None
    assert session.session_id is not None
    assert session.credentials_version == user.credentials_version

def test_login_invalid_credentials():
    email = f"user_{secrets.token_hex(4)}@example.com"
    password = "secure_password"
    
    auth.register.execute(email, password)
    
    with pytest.raises(InvalidCredentialsError):
        auth.login.execute(email, "wrong_password")

def test_change_password():
    email = f"user_{secrets.token_hex(4)}@example.com"
    old_password = "old_password"
    new_password = "new_password"
    
    user = auth.register.execute(email, old_password)
    
    auth.change_password.execute(user.id, old_password, new_password)
    
    # Should login with new password
    session = auth.login.execute(email, new_password)
    assert session is not None
    
    # Old password should fail
    with pytest.raises(InvalidCredentialsError):
        auth.login.execute(email, old_password)

def test_delete_account():
    email = f"user_{secrets.token_hex(4)}@example.com"
    password = "secure_password"
    
    user = auth.register.execute(email, password)
    
    auth.delete_account.execute(user.id)
    
    with pytest.raises(InvalidCredentialsError):
        auth.login.execute(email, password)

def test_logout():
    email = f"user_{secrets.token_hex(4)}@example.com"
    password = "secure_password"
    
    user = auth.register.execute(email, password)
    session = auth.login.execute(email, password)
    
    auth.logout.execute(user.id, session.session_id)
    # Verify session is revoked (in memory implementation check)
    # The Facade doesn't expose verification directly, need to check adapter
    assert not auth._adapters.session_service.verify(session.token, user.credentials_version)
