import pytest , pytest_asyncio
from uuid import uuid4
from authkit import (
    RegistrationUseCase,
    LoginUseCase,
    LogoutUseCase,
    LogoutAllUseCase,
)
from authkit.exceptions import AuthError
from tests.container import load


# --------------------------------------------------
# Core fixtures
# --------------------------------------------------

@pytest.fixture
def services():
    auth_container = load()
    return {
        "passwords": auth_container["password_manager"],
        "tokens": auth_container["token_service"],
        "user_repo": auth_container["user_repo"],
    }


@pytest_asyncio.fixture
async def registered_user(services):
    uc = RegistrationUseCase(services["user_repo"], services["passwords"])
    return await uc.execute("test@example.com", "secret")


@pytest_asyncio.fixture
async def logged_in_token(services, registered_user):
    uc = LoginUseCase(services["user_repo"], services["passwords"], services["tokens"])
    return await uc.execute("test@example.com", "secret")


# --------------------------------------------------
# Logout (single token)
# --------------------------------------------------

@pytest.mark.asyncio
async def test_logout_single_token_success(
    services, registered_user, logged_in_token
):
    logout_uc = LogoutUseCase(services["tokens"])

    await logout_uc.execute(
        user_id=registered_user.id,
        token_id=logged_in_token.token_id,
    )

    # token must be invalid after logout
    assert not await services["tokens"].verify(logged_in_token.token,registered_user.credentials_version)


@pytest.mark.asyncio
async def test_logout_single_token_twice_is_idempotent(
    services, registered_user, logged_in_token
):
    logout_uc = LogoutUseCase(services["tokens"])

    await logout_uc.execute(
        user_id=registered_user.id,
        token_id=logged_in_token.token_id,
    )

    # second logout should not error
    await logout_uc.execute(
        user_id=registered_user.id,
        token_id=logged_in_token.token_id,
    )

    assert not await services["tokens"].verify(logged_in_token.token, registered_user.credentials_version)


@pytest.mark.asyncio
async def test_logout_single_token_invalid_token_id(
    services, registered_user
):
    logout_uc = LogoutUseCase(services["tokens"])

    with pytest.raises(AuthError):
        await logout_uc.execute(
            user_id=registered_user.id,
            token_id=uuid4(),
        )


# --------------------------------------------------
# Logout ALL tokens
# --------------------------------------------------

@pytest.mark.asyncio
async def test_logout_all_revokes_all_tokens(
    services, registered_user
):
    login_uc = LoginUseCase(services["user_repo"], services["passwords"], services["tokens"])

    token1 = await login_uc.execute("test@example.com", "secret")
    token2 = await login_uc.execute("test@example.com", "secret")

    logout_all_uc = LogoutAllUseCase(services["user_repo"], services["tokens"])
    await logout_all_uc.execute(registered_user.id)

    assert not await services["tokens"].verify(token1.token , registered_user.credentials_version)
    assert not await services["tokens"].verify(token2.token, registered_user.credentials_version)


@pytest.mark.asyncio
async def test_logout_all_increments_credentials_version(
    services, registered_user
):
    repo = services["user_repo"]
    initial_version = registered_user.credentials_version

    logout_all_uc = LogoutAllUseCase(repo, services["tokens"])
    await logout_all_uc.execute(registered_user.id)

    updated = await repo.get_by_identifier("test@example.com")
    assert updated.credentials_version == initial_version + 1


@pytest.mark.asyncio
async def test_logout_all_called_twice_is_safe(
    services, registered_user
):
    repo = services["user_repo"]
    initial_version = registered_user.credentials_version

    logout_all_uc = LogoutAllUseCase(repo, services["tokens"])

    await logout_all_uc.execute(registered_user.id)
    await logout_all_uc.execute(registered_user.id)

    updated = await repo.get_by_identifier("test@example.com")

    assert updated.credentials_version == initial_version + 2


@pytest.mark.asyncio
async def test_logout_all_invalid_user(
    services
):
    logout_all_uc = LogoutAllUseCase(services["user_repo"], services["tokens"])

    with pytest.raises(AuthError):
        await logout_all_uc.execute(uuid4())


# --------------------------------------------------
# Interaction between logout & logout-all
# --------------------------------------------------

@pytest.mark.asyncio
async def test_logout_all_invalidates_existing_tokens(
    services, registered_user
):
    repo = services["user_repo"]
    login_uc = LoginUseCase(repo, services["passwords"], services["tokens"])
    token = await login_uc.execute("test@example.com", "secret")

    logout_all_uc = LogoutAllUseCase(repo, services["tokens"])
    await logout_all_uc.execute(registered_user.id)

    assert not await services["tokens"].verify(token.token, registered_user.credentials_version)


@pytest.mark.asyncio
async def test_logout_after_logout_all_is_noop(
    services, registered_user
):
    repo = services["user_repo"]
    login_uc = LoginUseCase(repo, services["passwords"], services["tokens"])
    token = await login_uc.execute("test@example.com", "secret")

    logout_all_uc = LogoutAllUseCase(repo, services["tokens"])
    await logout_all_uc.execute(registered_user.id)

    logout_uc = LogoutUseCase(services["tokens"])

    # should not error even though token is already invalid
    await logout_uc.execute(
        user_id=registered_user.id,
        token_id=token.token_id,
    )

    assert not await services["tokens"].verify(token.token, registered_user.credentials_version)
