import pytest , pytest_asyncio
from uuid import uuid4

from authkit import (
    ChangePasswordUseCase,
    RegistrationUseCase,
    LoginUseCase,
)
from authkit.exceptions import (
    NotFoundError,
    InvalidCredentialsError,
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
    repo = services["user_repo"]
    passwords = services["passwords"]
    
    reg_uc = RegistrationUseCase(repo, passwords)
    user = await reg_uc.execute("test@example.com", "old-secret")

    return repo, user, services


@pytest.mark.asyncio
async def test_change_password_success(registered_user):
    repo, user, services = registered_user
    passwords = services["passwords"]
    tokens = services["tokens"]

    uc = ChangePasswordUseCase(repo, passwords, tokens)

    await uc.execute(
        user_id=user.id,
        old_password="old-secret",
        new_password="new-secret",
    )

    updated = await repo.get_by_id(user.id)

    assert updated.credentials_version == user.credentials_version + 1
    assert updated.password_hash != user.password_hash
    assert await passwords.verify("new-secret", updated.password_hash)


@pytest.mark.asyncio
async def test_change_password_invalid_old_password(registered_user):
    repo, user, services = registered_user
    passwords = services["passwords"]
    tokens = services["tokens"]

    uc = ChangePasswordUseCase(repo, passwords, tokens)

    with pytest.raises(InvalidCredentialsError):
        await uc.execute(
            user_id=user.id,
            old_password="wrong-password",
            new_password="new-secret",
        )


@pytest.mark.asyncio
async def test_change_password_user_not_found(services):
    uc = ChangePasswordUseCase(
        services["user_repo"],
        services["passwords"],
        services["tokens"],
    )

    with pytest.raises(NotFoundError):
        await uc.execute(
            user_id=uuid4(),
            old_password="old-secret",
            new_password="new-secret",
        )


@pytest.mark.asyncio
async def test_change_password_revokes_existing_tokens(registered_user):
    repo, user, services = registered_user
    passwords = services["passwords"]
    tokens = services["tokens"]

    login_uc = LoginUseCase(repo, passwords, tokens)
    token = await login_uc.execute("test@example.com", "old-secret")

    assert await tokens.verify(token.token , user.credentials_version)

    uc = ChangePasswordUseCase(repo, passwords, tokens)
    await uc.execute(user.id, "old-secret", "new-secret")

    updated_user = await repo.get_by_id(user.id)

    assert not await tokens.verify(token.token,updated_user.credentials_version)


@pytest.mark.asyncio
async def test_change_password_cannot_reuse_same_password(registered_user):
    repo, user, services = registered_user
    passwords = services["passwords"]
    tokens = services["tokens"]

    uc = ChangePasswordUseCase(repo, passwords, tokens)

    with pytest.raises(InvalidCredentialsError):
        await uc.execute(
            user_id=user.id,
            old_password="old-secret",
            new_password="old-secret",
        )
