import pytest
import pytest_asyncio
from uuid import UUID, uuid4
from authkit import (
    LoginCQRSUseCase,
    StartLoginWithOTPUseCase,
    VerifyLoginCQRSWithOTPUseCase,
    RegistrationUseCase,
    OTPPurpose,
)
from authkit.exceptions.auth import InvalidCredentialsError, InvalidOTPError
from tests.container import load

# -------------------------------------------------------------------------
# Fixtures
# -------------------------------------------------------------------------

@pytest.fixture
def services():
    """
    Provides the DI container services for testing.
    """
    auth_container = load()
    return {
        "passwords": auth_container["password_manager"],
        "tokens": auth_container["token_service"],
        "otp_store": auth_container["otp_store"],
        "otp_manager": auth_container["otp_manager"],
        "intent": auth_container["user_id_intent_store"],
        "user_repo": auth_container["user_repo"],
        "user_reader": auth_container["user_reader"],
        "user_writer": auth_container["user_writer"],
    }

@pytest_asyncio.fixture
async def registered_user(services):
    """
    Ensures a standard test user exists in the repository.
    """
    uc = RegistrationUseCase(services["user_writer"], services["passwords"])
    return await uc.execute("test@example.com", "secret")

# -------------------------------------------------------------------------
# LoginCQRSUseCase (Direct Login)
# -------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_should_return_auth_token_on_valid_credentials(services, registered_user):
    """
    Expectation:
        When a user provides valid email and password credentials, 
        the system should return a valid Authentication Token containing the access token and token ID.
    """
    uc = LoginCQRSUseCase(
        services["user_reader"],
        services["user_writer"],
        services["passwords"],
        services["tokens"],
    )
    
    token = await uc.execute(registered_user.identifier, "secret")
    
    assert token.token is not None
    assert token.token_id is not None

@pytest.mark.asyncio
async def test_should_raise_error_when_password_is_invalid(services, registered_user):
    """
    Expectation:
        When a user provides an incorrect password for a valid email,
        the system should raise an `InvalidCredentialsError` to indicate authentication failure.
    """
    uc = LoginCQRSUseCase(
        services["user_reader"],
        services["user_writer"],
        services["passwords"],
        services["tokens"],
    )
    
    with pytest.raises(InvalidCredentialsError):
        await uc.execute(registered_user.identifier, "wrong_password")

@pytest.mark.asyncio
async def test_should_raise_error_when_user_is_unknown(services):
    """
    Expectation:
        When a user provides an email address that is not registered,
        the system should raise an `InvalidCredentialsError` (security best practice: do not reveal user existence).
    """
    uc = LoginCQRSUseCase(
        services["user_reader"],
        services["user_writer"],
        services["passwords"],
        services["tokens"],
    )
    
    with pytest.raises(InvalidCredentialsError):
        await uc.execute("unknown@example.com", "secret")

# -------------------------------------------------------------------------
# StartLoginWithOTPUseCase (Start 2FA)
# -------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_should_return_verification_token_and_store_otp_on_valid_credentials(services, registered_user):
    """
    Expectation:
        When a user with valid credentials initiates a login requiring OTP (MFA),
        the system should:
        1. Return a unique `VerificationToken`.
        2. Generate and securely store an OTP code linked to that token.
    """
    uc = StartLoginWithOTPUseCase(
        services["user_reader"],
        services["passwords"],
        services["intent"],
        services["otp_store"],
        services["otp_manager"],
    )
    
    verification_token = await uc.execute("test@example.com", "secret")
    
    # Assert return value
    assert isinstance(verification_token, UUID)
    
    # Assert Side Effect: OTP is stored and retrievable
    otp_code = await services["otp_store"].get(verification_token, OTPPurpose.MFA)
    assert otp_code is not None
    assert len(otp_code) > 0

@pytest.mark.asyncio
async def test_should_raise_error_when_starting_otp_with_invalid_credentials(services, registered_user):
    """
    Expectation:
        When attempting to start an OTP login flow with invalid credentials (e.g., wrong password),
        the system should raise an `InvalidCredentialsError` and NOT generate an OTP or token.
    """
    uc = StartLoginWithOTPUseCase(
        services["user_reader"],
        services["passwords"],
        services["intent"],
        services["otp_store"],
        services["otp_manager"],
    )
    
    with pytest.raises(InvalidCredentialsError):
        await uc.execute("test@example.com", "wrong_password")

# -------------------------------------------------------------------------
# VerifyLoginCQRSWithOTPUseCase (Complete 2FA)
# -------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_should_return_auth_token_on_valid_otp_verification(services, registered_user):
    """
    Expectation:
        When a valid `VerificationToken` and the corresponding correct OTP code are provided,
        the system should complete the login process and return a valid Authentication Token.
    """
    # Arrange
    verification_token = uuid4()
    otp_code = "123456"
    user_id = registered_user.id
    
    # Seed the stores
    # await services["intent"].store(verification_token, user_id)  # Link token -> user
    services["intent"].intents[verification_token] = user_id
    await services["otp_store"].store(verification_token, otp_code, OTPPurpose.MFA)
    
    uc = VerifyLoginCQRSWithOTPUseCase(
        services["user_reader"],
        services["user_writer"],
        services["intent"],
        services["tokens"],
        services["otp_store"],
    )
    
    # Act
    auth_token = await uc.execute(verification_token, otp_code)
    
    # Assert
    assert auth_token.token is not None

@pytest.mark.asyncio
async def test_should_raise_error_when_otp_code_is_invalid(services, registered_user):
    """
    Expectation:
        When a valid `VerificationToken` is provided but the OTP code does not match the stored one,
        the system should raise an `InvalidOTPError`.
    """
    # Arrange
    verification_token = uuid4()
    correct_otp = "123456"
    # await services["intent"].store(verification_token, registered_user.id)
    services["intent"].intents[verification_token] = registered_user.id
    await services["otp_store"].store(verification_token, correct_otp, OTPPurpose.MFA)
    
    uc = VerifyLoginCQRSWithOTPUseCase(
        services["user_reader"],
        services["user_writer"],
        services["intent"],
        services["tokens"],
        services["otp_store"],
    )
    
    # Act & Assert
    with pytest.raises(InvalidOTPError):
        await uc.execute(verification_token, "wrong_code")

@pytest.mark.asyncio
async def test_should_raise_error_when_verification_token_is_invalid(services):
    """
    Expectation:
        When verifying an OTP with a `VerificationToken` that does not exist or has expired,
        the system should raise an `InvalidOTPError`.
    """
    uc = VerifyLoginCQRSWithOTPUseCase(
        services["user_reader"],
        services["user_writer"],
        services["intent"],
        services["tokens"],
        services["otp_store"],
    )
    
    with pytest.raises(InvalidOTPError):
        await uc.execute(uuid4(), "123456")
