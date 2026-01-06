import pytest
from uuid import uuid4
from authkit.core.adapters import AuthAdapters
from authkit import AuthKit
from tests.fakes import FakeSessionService, FakePasswordManager, FakeUserRepository

def test_cqrs_mode_wiring():
    """
    Verifies that when specific reader and writer repositories are provided (CQRS mode),
    AuthKit correctly routes read operations to the reader and write operations to the writer.
    """
    # 1. Setup separate repositories for Read and Write
    reader_repo = FakeUserRepository()
    writer_repo = FakeUserRepository()
    
    # 2. Configure Adapters in CQRS mode
    adapters = AuthAdapters(
        session_service=FakeSessionService(),
        password_manager=FakePasswordManager(),
        user_reader=reader_repo,
        user_writer=writer_repo
        # user_repo is None by default
    )
    
    auth = AuthKit(adapters=adapters)
    
    # 3. Test: Registration should write to WRITER_REPO
    email = "cqrs_user@example.com"
    password = "password"
    
    auth.register.execute(email, password)
    
    # Assertion: User should exist in Writer, but NOT in Reader (since they are disconnected fakes)
    assert writer_repo.get_by_identifier(email) is not None
    assert reader_repo.get_by_identifier(email) is None
    
    # 4. Test: Login should read from READER_REPO
    # Since the user is not in reader_repo, login should fail (proving it looked at reader)
    from authkit.exceptions import InvalidCredentialsError
    with pytest.raises(InvalidCredentialsError):
        auth.login.execute(email, password)
        
    # 5. Manual Sync (Simulate Eventual Consistency)
    # If we manually add the user to the reader, login should then work
    user_data = writer_repo.get_by_identifier(email)
    reader_repo.add(user_data) # Manually copy
    
    session = auth.login.execute(email, password)
    assert session.token is not None

def test_unified_mode_wiring():
    """
    Verifies that when a single user_repo is provided (Unified mode),
    it is used for both reading and writing.
    """
    repo = FakeUserRepository()
    
    adapters = AuthAdapters(
        session_service=FakeSessionService(),
        password_manager=FakePasswordManager(),
        user_repo=repo
    )
    
    assert adapters.user_reader is repo
    assert adapters.user_writer is repo
    
    auth = AuthKit(adapters=adapters)
    
    email = "unified_user@example.com"
    auth.register.execute(email, "password")
    
    # Should automatically be available for login since it's the same repo
    session = auth.login.execute(email, "password")
    assert session.token is not None

def test_adapter_validation_partial_is_allowed():
    """
    Verifies that we CAN initialize AuthAdapters with missing repos (Partial Config pattern).
    """
    adapters = AuthAdapters(
        session_service=FakeSessionService(),
        password_manager=FakePasswordManager(),
        # No user_repo, and no reader/writer pair
    )
    
    assert adapters.user_reader is None
    assert adapters.user_writer is None

def test_adapter_validation_partial_cqrs_is_allowed():
    """
    Verifies that providing only one of reader/writer is technically valid logic-wise during init,
    though it might fail later during execution if the specific use case needs the missing one.
    """
    adapters = AuthAdapters(
        session_service=FakeSessionService(),
        password_manager=FakePasswordManager(),
        user_reader=FakeUserRepository()
    )
    
    assert adapters.user_reader is not None
    assert adapters.user_writer is None

def test_adapter_validation_ambiguous_config():
    """
    Verifies that AuthAdapters raises a ValueError if BOTH user_repo and reader/writer are provided.
    """
    repo = FakeUserRepository()
    with pytest.raises(ValueError) as excinfo:
        AuthAdapters(
            session_service=FakeSessionService(),
            password_manager=FakePasswordManager(),
            user_repo=repo,
            user_reader=FakeUserRepository(), # Different instance
            user_writer=repo
        )
    
    assert "Ambiguous configuration" in str(excinfo.value)
