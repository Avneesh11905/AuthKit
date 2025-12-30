from tests.fakes.passwd_manager import FakePasswordManager
from tests.fakes.token_service import FakeTokenService
from tests.fakes.otp.otp_manager import FakeOTPManager
from tests.fakes.otp.otp_store import FakeOTPStore
from tests.fakes.intents.user_id_intent_store import FakeUserIDIntentStore
from tests.fakes.intents.user_id_intent_store import FakeUserIDIntentStore
from tests.fakes.intents.registration_intent_store import FakeRegistrationIntentStore
from tests.fakes.user_repo import FakeUserRepository
from tests.fakes.user_repo_cqrs.user_reader_repo import FakeUserReaderRepository
from tests.fakes.user_repo_cqrs.user_writer_repo import FakeUserWriterRepository
from typing import Any , Callable

class FakeContainer:
    def __init__(self):
        self.services: dict[str,tuple[Callable[[],Any],bool]] = {}
        self.singletons = {}
    
    def register(self, service: str, factory: Callable[[],Any], singleton: bool = False):
        self.services[service] = (factory, singleton)
    
    def __getitem__(self, service: str):
        if service in self.singletons:
            return self.singletons[service]
        if service not in self.services:
            raise KeyError(f"Service {service} not registered")
        factory, singleton = self.services[service]
        instance = factory()
        if singleton:
            self.singletons[service] = instance
        return instance

    def __del__(self):
        self.singletons = {}
        self.services = {}

from tests.fakes.user_repo_cqrs.user_store import FakeUserStore

def load():
    container = FakeContainer()
    container.register("password_manager", FakePasswordManager)
    container.register("token_service", FakeTokenService)
    container.register("user_id_intent_store", FakeUserIDIntentStore)
    container.register("register_intent_store", FakeRegistrationIntentStore)
    container.register("otp_store", FakeOTPStore)
    container.register("otp_manager", FakeOTPManager)
    container.register("user_repo", FakeUserRepository)
    
    # Store isolation for CQRS repos
    # Create a fresh store for this container instance
    user_store = FakeUserStore()
    
    # Use lambdas to inject the *same* store instance into both repos
    container.register("user_reader", lambda: FakeUserReaderRepository(user_store))
    container.register("user_writer", lambda: FakeUserWriterRepository(user_store))
    
    return container