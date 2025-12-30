import pytest , pytest_asyncio
from authkit import ChangePasswordCQRSUseCase, RegistrationUseCase
from authkit.exceptions import InvalidCredentialsError
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
async def change_password_uc(services):
    return ChangePasswordCQRSUseCase(
        services["user_reader"],
        services["user_writer"],
        services["passwords"],
        services["tokens"]
    )

@pytest.mark.asyncio
async def test_cqrs_change_password_success(services, registered_user, change_password_uc):
    user_id = registered_user.id
    
    await change_password_uc.execute(user_id, "secret", "new_secret")
    
    # Verify new password works
    user = await services["user_reader"].get_by_id(user_id)
    assert await services["passwords"].verify("new_secret", user.password_hash)
    
    # Verify old password fails
    assert not await services["passwords"].verify("secret", user.password_hash)

@pytest.mark.asyncio
async def test_cqrs_change_password_invalid_old(registered_user, change_password_uc):
    user_id = registered_user.id
    
    with pytest.raises(InvalidCredentialsError):
        await change_password_uc.execute(user_id, "wrong", "new_secret")

@pytest.mark.asyncio
async def test_cqrs_change_password_same_as_old(registered_user, change_password_uc):
    user_id = registered_user.id
    
    with pytest.raises(InvalidCredentialsError):
        await change_password_uc.execute(user_id, "secret", "secret")
