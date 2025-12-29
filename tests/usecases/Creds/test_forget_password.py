import pytest, pytest_asyncio
from authkit import (
    StartForgetPasswordUseCase,
    VerifyForgetPasswordUseCase,
    RegistrationUseCase,
    OTPPurpose,
)
from authkit.exceptions import AuthError
from tests.container import load

@pytest.fixture
def services():
    container = load()
    return {
        "passwords": container["password_manager"],
        "user_repo": container["user_repo"],
        "intent": container["user_id_intent_store"],
        "tokens": container["token_service"],
        "otp_store": container["otp_store"],
        "otp_manager": container["otp_manager"],
    }

@pytest_asyncio.fixture
async def registered_user(services):
    uc = RegistrationUseCase(services["user_repo"], services["passwords"])
    return await uc.execute("test@example.com", "secret")

@pytest.mark.asyncio
async def test_forget_password_start(services, registered_user):
    uc = StartForgetPasswordUseCase(
        services["user_repo"],
        services["tokens"],
        services["otp_store"],
        services["otp_manager"],
        services["intent"],
    )
    
    intent_token = await uc.execute("test@example.com")
    
    assert intent_token is not None
    
    # Verify OTP was stored
    otp = await services["otp_store"].get(intent_token, OTPPurpose.FORGET_PASSWORD)
    assert otp is not None

@pytest.mark.asyncio
async def test_forget_password_verify(services, registered_user):
    # Start flow
    start_uc = StartForgetPasswordUseCase(
        services["user_repo"],
        services["tokens"],
        services["otp_store"],
        services["otp_manager"],
        services["intent"],
    )
    intent_token = await start_uc.execute("test@example.com")
    otp = await services["otp_store"].get(intent_token, OTPPurpose.FORGET_PASSWORD)
    
    # Verify flow
    verify_uc = VerifyForgetPasswordUseCase(
        services["user_repo"],
        services["tokens"],
        services["passwords"],
        services["intent"],
        services["otp_store"],
        services["otp_manager"],
    )
    
    await verify_uc.execute(intent_token, otp, "new-password")
    
    # Verify password changed
    user = await services["user_repo"].get_by_identifier("test@example.com")
    assert await services["passwords"].verify("new-password", user.password_hash)

@pytest.mark.asyncio
async def test_forget_password_verify_invalid_otp(services, registered_user):
    start_uc = StartForgetPasswordUseCase(
        services["user_repo"],
        services["tokens"],
        services["otp_store"],
        services["otp_manager"],
        services["intent"],
    )
    intent_token = await start_uc.execute("test@example.com")
    
    verify_uc = VerifyForgetPasswordUseCase(
        services["user_repo"],
        services["tokens"],
        services["passwords"],
        services["intent"],
        services["otp_store"],
        services["otp_manager"],
    )
    
    with pytest.raises(AuthError):
        await verify_uc.execute(intent_token, "wrong", "new-password")


@pytest.mark.asyncio
async def test_forget_password_start_user_not_found(services):
    uc = StartForgetPasswordUseCase(
        services["user_repo"],
        services["tokens"],
        services["otp_store"],
        services["otp_manager"],
        services["intent"],
    )

    from authkit.exceptions import AuthError
    with pytest.raises(AuthError):
        await uc.execute("nonexistent@example.com")


@pytest.mark.asyncio
async def test_forget_password_verify_invalid_token(services):
    verify_uc = VerifyForgetPasswordUseCase(
        services["user_repo"],
        services["tokens"],
        services["passwords"],
        services["intent"],
        services["otp_store"],
        services["otp_manager"],
    )

    from uuid import UUID
    # Random UUID that shouldn't exist in intent store
    with pytest.raises(AuthError):
        await verify_uc.execute(UUID(int=0), "123456", "new-password")


@pytest.mark.asyncio
async def test_forget_password_revokes_tokens(services, registered_user):
    # Login to get a token
    from authkit import LoginUseCase
    login = LoginUseCase(services["user_repo"], services["passwords"], services["tokens"])
    token = await login.execute("test@example.com", "secret")

    # Start forget flow
    start_uc = StartForgetPasswordUseCase(
        services["user_repo"],
        services["tokens"],
        services["otp_store"],
        services["otp_manager"],
        services["intent"],
    )
    intent_token = await start_uc.execute("test@example.com")
    otp = await services["otp_store"].get(intent_token, OTPPurpose.FORGET_PASSWORD)

    # Verify flow
    verify_uc = VerifyForgetPasswordUseCase(
        services["user_repo"],
        services["tokens"],
        services["passwords"],
        services["intent"],
        services["otp_store"],
        services["otp_manager"],
    )
    
    await verify_uc.execute(intent_token, otp, "new-password")

    # Check token is revoked
    # Note: Credential version should have incremented, making old token invalid
    assert not await services["tokens"].verify(token.token, registered_user.credentials_version)
    
    # Reload user to check new version if needed, but verify() check with old version 
    # might pass if verify() implements checking against current user version from DB?
    # Usually verify() takes the version embedded in token or passes version from DB.
    # The fake token service likely compares the passed version.
    
    # Let's check the user's new version in DB
    updated_user = await services["user_repo"].get_by_identifier("test@example.com")
    assert updated_user.credentials_version > registered_user.credentials_version
    
    # And verify should fail even if we passed the OLD version? 
    # Actually, revoke_all typically updates the user's credential version in DB (which we checked).
    # TokenService.revoke_all might also blacklist.
    # But usually validation checks if token_version < user.credential_version.
    
    # Let's just assert the token verification returns False with the OLD version?
    # Wait, if I pass the old version to verify(), and the token has the old version, 
    # and it was not explicitly revoked by ID but by "revoke_all" (version bump)...
    # The FakeTokenService implementation needs to be checked.
    # If verify() just checks `token_claim.version == passed_version`...
    # The `revoke_all` implies bumping the version in User entity.
    # The `TokenService.verify` usually takes the version from `User` entity to compare against token.
    # In the test `verify(token, version)`, the version arg is usually the expected valid version (User's current version).
    
    # So if we pass the NEW version (from updated_user), the old token (with old version 0) should fail.
    assert not await services["tokens"].verify(token.token, updated_user.credentials_version)
