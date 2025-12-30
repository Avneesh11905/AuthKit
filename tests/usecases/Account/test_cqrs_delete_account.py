import pytest , pytest_asyncio
from authkit import DeleteAccountCQRSUseCase, RegistrationUseCase
from tests.container import load

@pytest.fixture
def services():
    auth_container = load()
    return {
        "passwords": auth_container["password_manager"],
        "tokens": auth_container["token_service"],
        "user_writer": auth_container["user_writer"],
        "user_reader": auth_container["user_reader"],
    }

@pytest_asyncio.fixture
async def registered_user(services):
    uc = RegistrationUseCase(services["user_writer"], services["passwords"])
    return await uc.execute("test@example.com", "secret")

@pytest_asyncio.fixture
async def delete_account_uc(services):
    return DeleteAccountCQRSUseCase(
        services["user_reader"],
        services["user_writer"],
        services["tokens"]
    )

@pytest.mark.asyncio
async def test_cqrs_delete_account_success(services, registered_user, delete_account_uc):
    user_id = registered_user.id
    
    # Verify user exists
    assert await services["user_reader"].get_by_id(user_id) is not None

    await delete_account_uc.execute(user_id)

    # Verify user is deleted (should return None)
    assert await services["user_reader"].get_by_id(user_id) is None

@pytest.mark.asyncio
async def test_cqrs_delete_non_existent_account(delete_account_uc, services):
    import uuid
    random_id = uuid.uuid4()
    
    # Should not raise error
    result = await delete_account_uc.execute(random_id)
    assert result == random_id
