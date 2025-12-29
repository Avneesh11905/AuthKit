import pytest , pytest_asyncio
from uuid import UUID
from authkit import (
    RegistrationUseCase,
    StartRegistrationWithOTPUseCase,
    VerifyRegistrationWithOTPUseCase,
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
        "otp_store": auth_container["otp_store"],
        "otp_manager": auth_container["otp_manager"],
        "intent": auth_container["register_intent_store"],
        "user_repo": auth_container["user_repo"],
    }

@pytest_asyncio.fixture
async def registration_started(services):
    uc = StartRegistrationWithOTPUseCase(
        services["user_repo"],
        services["passwords"],
        services["intent"],
        services["otp_store"],
        services["otp_manager"],
    )

    verification_token = await uc.execute("test@example.com", "secret")
    otp = await services["otp_store"].get(verification_token, OTPPurpose.REGISTRATION)

    return verification_token, otp


# -----------------------------
# Direct registration tests
# -----------------------------

@pytest.mark.asyncio
async def test_register_success(services):
    uc = RegistrationUseCase(services["user_repo"], services["passwords"])

    user = await uc.execute("test@example.com", "secret")

    assert user.identifier == "test@example.com"
    assert user.password_hash != "secret"
    assert user.credentials_version == 0

    stored = await services["user_repo"].get_by_identifier("test@example.com")
    assert stored is not None
    assert stored.id == user.id


@pytest.mark.asyncio
async def test_register_conflict(services):
    uc = RegistrationUseCase(services["user_repo"], services["passwords"])

    await uc.execute("test@example.com", "secret")

    with pytest.raises(AuthError):
        await uc.execute("test@example.com", "secret")


# -----------------------------
# Registration with OTP
# -----------------------------



@pytest.mark.asyncio
async def test_registration_with_otp_success(services, registration_started):
    verification_token, otp = registration_started

    uc = VerifyRegistrationWithOTPUseCase(
        services["user_repo"],
        services["intent"],
        services["otp_store"],
    )

    user = await uc.execute(verification_token, otp)

    assert user.identifier == "test@example.com"

    stored = await services["user_repo"].get_by_identifier("test@example.com")
    assert stored is not None
    assert stored.id == user.id


@pytest.mark.asyncio
async def test_registration_with_invalid_otp(services, registration_started):
    verification_token, _ = registration_started

    uc = VerifyRegistrationWithOTPUseCase(
        services["user_repo"],
        services["intent"],
        services["otp_store"],
    )

    with pytest.raises(AuthError):
        await uc.execute(verification_token, "wrong")


@pytest.mark.asyncio
async def test_registration_with_invalid_token(services):
    uc = VerifyRegistrationWithOTPUseCase(
        services["user_repo"],
        services["intent"],
        services["otp_store"],
    )

    with pytest.raises(AuthError):
        await uc.execute(UUID(int=0), "123456")


@pytest.mark.asyncio
async def test_registration_otp_single_use(services, registration_started):
    verification_token, otp = registration_started

    uc = VerifyRegistrationWithOTPUseCase(
        services["user_repo"],
        services["intent"],
        services["otp_store"],
    )

    await uc.execute(verification_token, otp)

    with pytest.raises(AuthError):
        await uc.execute(verification_token, otp)


@pytest.mark.asyncio
async def test_registration_intent_consumed_after_success(services, registration_started):
    verification_token, otp = registration_started

    uc = VerifyRegistrationWithOTPUseCase(
        services["user_repo"],
        services["intent"],
        services["otp_store"],
    )

    await uc.execute(verification_token, otp)

    assert await services["intent"].get(verification_token) is None
