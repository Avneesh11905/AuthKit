import pytest , pytest_asyncio
from uuid import UUID
from authkit import (
    LoginUseCase,
    StartLoginWithOTPUseCase,
    VerifyLoginWithOTPUseCase,
    RegistrationUseCase,
    OTPPurpose,
)
from authkit.exceptions import AuthError
from tests.container import load


# -----------------------------
# Core fixtures
# -----------------------------


@pytest.fixture
def services():
    auth_container = load()
    return {
        "passwords": auth_container["password_manager"],
        "tokens": auth_container["token_service"],
        "otp_store": auth_container["otp_store"],
        "otp_manager": auth_container["otp_manager"],
        "intent": auth_container["user_id_intent_store"],
        "user_repo": auth_container["user_repo"],
    }


@pytest_asyncio.fixture
async def registered_user(services):
    uc = RegistrationUseCase(services["user_repo"], services["passwords"])
    return await uc.execute("test@example.com", "secret")


@pytest_asyncio.fixture
async def login_uc(services, registered_user):
    return LoginUseCase(
        services["user_repo"],
        services["passwords"],
        services["tokens"],
    )

@pytest_asyncio.fixture
async def otp_login_started(services, registered_user):
    uc = StartLoginWithOTPUseCase(
        services["user_repo"],
        services["passwords"],
        services["intent"],
        services["otp_store"],
        services["otp_manager"],
    )

    verification_token = await uc.execute("test@example.com", "secret")
    otp = await services["otp_store"].get(verification_token, OTPPurpose.MFA)

    return verification_token, otp


# -----------------------------
# Password login tests
# -----------------------------

@pytest.mark.asyncio
async def test_login_success(login_uc):
    token = await login_uc.execute("test@example.com", "secret")
    assert token.token is not None
    assert token.token_id is not None


@pytest.mark.asyncio
async def test_login_invalid_password(login_uc):
    with pytest.raises(AuthError):
        await login_uc.execute("test@example.com", "wrong")


@pytest.mark.asyncio
async def test_login_invalid_identifier(login_uc):
    with pytest.raises(AuthError):
        await login_uc.execute("wrong@email.com", "secret")


# -----------------------------
# OTP login tests
# -----------------------------

@pytest.mark.asyncio
async def test_login_otp_success(services, otp_login_started):
    verification_token, otp = otp_login_started

    uc = VerifyLoginWithOTPUseCase(
        services["user_repo"],
        services["intent"],
        services["tokens"],
        services["otp_store"],
    )

    auth_token = await uc.execute(verification_token, otp)

    assert auth_token.token is not None
    assert auth_token.token_id is not None


@pytest.mark.asyncio
async def test_login_otp_invalid_code(services, otp_login_started):
    verification_token, _ = otp_login_started

    uc = VerifyLoginWithOTPUseCase(
        services["user_repo"],
        services["intent"],
        services["tokens"],
        services["otp_store"],
    )

    with pytest.raises(AuthError):
        await uc.execute(verification_token, "wrong")


@pytest.mark.asyncio
async def test_login_otp_invalid_verification_token(services):
    uc = VerifyLoginWithOTPUseCase(
        services["user_repo"],
        services["intent"],
        services["tokens"],
        services["otp_store"],
    )

    with pytest.raises(AuthError):
        await uc.execute(UUID(int=0), "123456")


@pytest.mark.asyncio
async def test_otp_is_single_use(services, otp_login_started):
    verification_token, otp = otp_login_started

    uc = VerifyLoginWithOTPUseCase(
        services["user_repo"],
        services["intent"],
        services["tokens"],
        services["otp_store"],
    )

    await uc.execute(verification_token, otp)

    with pytest.raises(AuthError):
        await uc.execute(verification_token, otp)


@pytest.mark.asyncio
async def test_login_intent_consumed_after_success(services, otp_login_started):
    verification_token, otp = otp_login_started

    uc = VerifyLoginWithOTPUseCase(
        services["user_repo"],
        services["intent"],
        services["tokens"],
        services["otp_store"],
    )

    await uc.execute(verification_token, otp)

    assert await services["intent"].get(verification_token) is None
