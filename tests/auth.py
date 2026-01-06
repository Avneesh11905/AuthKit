from authkit import AuthKit
from tests.fakes import (
    FakeSessionService,
    FakeRegistrationIntentStore,
    FakeUserRepository,
    FakePasswordManager,
    FakeUserIDIntentStore,
    FakeOTPManager,
    FakeOTPStore,
    FakeUserReaderRepository,
    FakeUserWriterRepository,
    FakeUserStore
)

store = FakeUserStore()


auth = AuthKit(
    session_service=FakeSessionService(),
    password_manager=FakePasswordManager(),

    # user_repo=FakeUserRepository(),
    user_reader=FakeUserReaderRepository(store),
    user_writer=FakeUserWriterRepository(store),

    otp_store=FakeOTPStore(),
    otp_manager=FakeOTPManager(),

    intent_store=FakeUserIDIntentStore(),
    registration_intent_store=FakeRegistrationIntentStore(),
)
print(auth.register.execute(identifier="test@example.com", password="password"))
print(auth.login.execute(identifier="test@example.com", password="password"))

