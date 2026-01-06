import pytest
from uuid import uuid4
from tests.auth import auth
from authkit.exceptions import InvalidCredentialsError
from authkit.domain import OTPPurpose

def test_login_with_otp_flow():
    # 1. Register User
    email = f"otp_user_{uuid4()}@example.com"
    password = "secure_password"
    auth.register.execute(email, password)
    # 2. Start Login with OTP
    verification_token = auth.login_otp_start.execute(email, password)
    assert verification_token is not None
    
    # 3. Retrieve OTP (Simulating user getting it from email/sms)
    # We access the otp_store via adapters/auth facade for testing
    otp_code = auth._adapters.otp_store.get(verification_token, OTPPurpose.MFA)
    assert otp_code is not None
    
    # 4. Verify Login with OTP
    session = auth.login_otp_verify.execute(verification_token, otp_code)
    assert session.token is not None
    assert not auth._adapters.otp_store.get(verification_token, OTPPurpose.MFA), "OTP should be consumed"

def test_forget_password_flow():
    # 1. Register User
    email = f"forget_pass_{uuid4()}@example.com"
    old_password = "old_password"
    auth.register.execute(email, old_password)
    
    # 2. Start Forget Password
    verification_token = auth.forget_password_start.execute(email)
    assert verification_token is not None
    
    # 3. Retrieve OTP 
    otp_code = auth._adapters.otp_store.get(verification_token, OTPPurpose.FORGET_PASSWORD)
    assert otp_code is not None
    
    # 4. Verify & Reset Password
    new_password = "new_secure_password"
    auth.forget_password_verify.execute(verification_token, otp_code, new_password)
    
    # 5. Verify old password no longer works
    with pytest.raises(InvalidCredentialsError):
        auth.login.execute(email, old_password)
        
    # 6. Verify new password works
    session = auth.login.execute(email, new_password)
    assert session.token is not None

def test_logout_all_flow():
    # 1. Register
    email = f"logout_all_{uuid4()}@example.com"
    password = "password"
    user = auth.register.execute(email, password)
    
    # 2. Create multiple sessions
    session1 = auth.login.execute(email, password)
    session2 = auth.login.execute(email, password)
    
    # 3. Logout All
    auth.logout_all.execute(user.id)
    
    # 4. Verify revocation
    assert not auth._adapters.session_service.verify(session1.token, session1.credentials_version) # Note: creds version might have bumped
    # Actually, verify checks creds version match. LogoutAll bumps creds version in the user entity.
    # The session service might still think the token is valid if it only checks a static list, 
    # but the verify logic in our fake matches stored creds version vs token creds version.
    
    # Let's verify via the service's verify method which should fail because version mismatch
    # We need to fetch the updated user to get the new creds version for a proper check if we were iterating sessions,
    # but the service.verify takes (token, current_user_creds_version).
    
    updated_user = auth._adapters.user_reader.get_by_id(user.id)
    assert not auth._adapters.session_service.verify(session1.token, updated_user.credentials_version)
    assert not auth._adapters.session_service.verify(session2.token, updated_user.credentials_version)

def test_logout_all_with_otp_flow():
    # 1. Register
    email = f"logout_all_otp_{uuid4()}@example.com"
    password = "password"
    user = auth.register.execute(email, password)
    
    # 2. Login
    session = auth.login.execute(email, password)
    user_id = user.id
    
    # 3. Start Logout All with OTP
    # Note: Requires an active session to initiate? No, usually public endpoint but requires ID.
    # The use case `StartLogoutAllWithOTPUseCase` takes `user_id`.
    verification_token = auth.logout_all_otp_start.execute(user_id)
    
    # 4. Get OTP
    otp_code = auth._adapters.otp_store.get(verification_token, OTPPurpose.MFA)
    
    # 5. Verify
    auth.logout_all_otp_verify.execute(verification_token, otp_code)
    
    # 6. Check Token Revocation
    updated_user = auth._adapters.user_reader.get_by_id(user_id)
    assert not auth._adapters.session_service.verify(session.token, updated_user.credentials_version)
    
from uuid import UUID

def test_registration_with_otp_flow():
    # 1. Start Registration with OTP
    email = f"reg_otp_{uuid4()}@example.com"
    password = "secure_password"
    
    # We expect a verification token back
    verification_token = auth.register_otp_start.execute(email, password)
    assert verification_token is not None
    assert isinstance(verification_token, UUID)

    # 2. Retrieve OTP (Simulating user getting it)
    otp_code = auth._adapters.otp_store.get(verification_token, OTPPurpose.REGISTRATION)
    assert otp_code is not None

    # 3. Verify Registration with OTP
    user = auth.register_otp_verify.execute(verification_token, otp_code)
    
    # 4. Assert User Created
    assert user is not None
    assert user.identifier == email
    
    # 5. Verify we can login now
    session = auth.login.execute(email, password)
    assert session.token is not None

def test_delete_account_with_otp_flow():
    # 1. Register User
    email = f"delete_otp_{uuid4()}@example.com"
    password = "password"
    user = auth.register.execute(email, password)
    user_id = user.id
    
    # Check user exists
    assert auth._adapters.user_reader.get_by_id(user_id) is not None

    # 2. Start Delete Account with OTP
    verification_token = auth.delete_account_otp_start.execute(user_id)
    assert verification_token is not None
    
    # 3. Get OTP
    otp_code = auth._adapters.otp_store.get(verification_token, OTPPurpose.MFA)
    assert otp_code is not None
    
    # 4. Verify & Delete
    result_id = auth.delete_account_otp_verify.execute(verification_token, otp_code)
    assert result_id == user_id
    
    # 5. Check User Deleted
    assert auth._adapters.user_reader.get_by_id(user_id) is None
    
    # 6. Check intent cleaned up given usage
    # (Optional implementation detail check)
    assert auth._adapters.otp_store.get(verification_token, OTPPurpose.MFA) is None
