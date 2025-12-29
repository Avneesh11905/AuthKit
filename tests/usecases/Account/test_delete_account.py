import pytest , pytest_asyncio
from uuid import uuid4

from authkit import (
    RegistrationUseCase,
    LoginUseCase,
    DeleteAccountUseCase,
)
from tests.container import load


@pytest.fixture
def services():
    container = load()
    return {
        "passwords": container["password_manager"],
        "tokens": container["token_service"],
        "user_repo": container["user_repo"],
    }


@pytest_asyncio.fixture
async def registered_user(services):
    uc = RegistrationUseCase(services["user_repo"], services["passwords"])
    user = await uc.execute("test@example.com", "secret")
    return user


@pytest_asyncio.fixture
async def logged_in_token(services, registered_user):
    login_uc = LoginUseCase(services["user_repo"], services["passwords"], services["tokens"])
    token = await login_uc.execute("test@example.com", "secret")
    return token


# -------------------------
# Core behavior
# -------------------------

@pytest.mark.asyncio
async def test_delete_account_success(
    services, registered_user, logged_in_token
):
    repo = services["user_repo"]
    delete_uc = DeleteAccountUseCase(repo, services["tokens"])

    await delete_uc.execute(registered_user.id)

    # user is gone
    user = await repo.get_by_id(registered_user.id)
    assert user is None

    # token is revoked
    valid = await services["tokens"].verify(logged_in_token.token,registered_user.credentials_version)
    assert not valid


# -------------------------
# Idempotency & safety
# -------------------------

@pytest.mark.asyncio
async def test_delete_account_twice_is_safe(
    services, registered_user, logged_in_token
):
    repo = services["user_repo"]
    delete_uc = DeleteAccountUseCase(repo, services["tokens"])

    await delete_uc.execute(registered_user.id)
    await delete_uc.execute(registered_user.id)  # second call

    user = await repo.get_by_id(registered_user.id)
    assert user is None

    valid = await services["tokens"].verify(logged_in_token.token,registered_user.credentials_version)
    assert not valid


@pytest.mark.asyncio
async def test_delete_non_existent_user_is_noop(
    services
):
    delete_uc = DeleteAccountUseCase(services["user_repo"], services["tokens"])

    # should not raise
    await delete_uc.execute(uuid4())


# -------------------------
# Token safety
# -------------------------

@pytest.mark.asyncio
async def test_delete_account_revokes_multiple_tokens(
    services, registered_user
):
    repo = services["user_repo"]
    login_uc = LoginUseCase(repo, services["passwords"], services["tokens"])

    token1 = await login_uc.execute("test@example.com", "secret")
    token2 = await login_uc.execute("test@example.com", "secret")

    delete_uc = DeleteAccountUseCase(repo, services["tokens"])
    await delete_uc.execute(registered_user.id)

    assert not await services["tokens"].verify(token1.token,registered_user.credentials_version)
    assert not await services["tokens"].verify(token2.token,registered_user.credentials_version)
