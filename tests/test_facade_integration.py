import pytest
from authkit import AuthKit
from tests.fakes import FakeSessionService, FakeUserRepository, FakePasswordManager

def test_direct_initialization():
    """
    Test that AuthKit can be initialized directly with dependencies,
    skipping manual AuthAdapters creation.
    """
    repo = FakeUserRepository()
    
    # Direct Init
    auth = AuthKit(
        user_repo=repo,
        password_manager=FakePasswordManager(),
        session_service=FakeSessionService()
    )
    
    # Check if registered use cases are functional
    assert hasattr(auth, 'login')
    auth.register.execute("user@example.com", "pass")
    assert repo.get_by_identifier("user@example.com") is not None

def test_mutable_configure():
    """
    Test that auth.configure() updates the instance in place.
    """
    # 1. Configure static deps
    auth = AuthKit(
        password_manager=FakePasswordManager()
    )
    
    # 2. Configure dynamic deps (mutates auth)
    repo = FakeUserRepository()
    auth.configure(
        user_repo=repo,
        session_service=FakeSessionService()
    )
    
    # Functional Check
    assert hasattr(auth, 'login')
    auth.register.execute("mutable@example.com", "pass")
    assert repo.get_by_identifier("mutable@example.com") is not None

def test_init_allows_empty():
    """
    AuthKit() with no arguments should be valid (Template Pattern).
    It initializes with empty/default adapters.
    """
    auth = AuthKit()
    assert hasattr(auth, 'login')
    # But using it might fail if dependencies are missing
    from authkit.exceptions import FeatureNotConfiguredError
    with pytest.raises(FeatureNotConfiguredError):
        auth.login.execute("x", "y")
