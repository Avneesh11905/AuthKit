# AuthKit 🔒

**Secure, Type-Safe, and Extensible Authentication for Python Applications.**

AuthKit is a clean-architecture authentication library designed for flexibility. It decouples your business logic from the underlying storage mechanism (SQL, NoSQL, In-Memory) using the **Ports and Adapters** pattern, while providing a developer-friendly **Facade** for everyday use.

## ✨ Features

*   **⚡ Unified Facade API**: Easy-to-use `AuthKit` class entry point.
*   **🔌 Storage Agnostic**: Swap databases without changing a line of business logic.
*   **🛡️ Type-Safe**: Fully typed with strict Mypy compliance and `.pyi` stubs for excellent IDE support.
*   **🔐 MFA / OTP**: Built-in support for Multi-Factor Authentication flows (Login, Registration, Account Deletion).
*   **🏗️ Clean Architecture**: Strict separation of Use Cases (Interactors), Entities, and Ports.
*   **🧩 Extensible**: Add custom use cases and inject your own dependencies easily.

### Core Capabilities
*   **Authentication**: Login (Password, OTP via Email/SMS), Logout.
*   **Registration**: Sign up with optimal verification flows.
*   **Account Management**: Change Password, Forgot Password, Delete Account (with OTP verification).
*   **Security**: Logout All Sessions, credential versioning.

## 📦 Installation

Since AuthKit is not yet on PyPI, you can install it directly from the source:

```bash
git clone https://github.com/Avneesh11905/AuthKit.git
cd AuthKit
pip install .
```

## 🚀 Quick Start

AuthKit runs out-of-the-box with any implementation of its `Ports`.

```python
from authkit import AuthKit
# See 'examples/quickstart.py' for a full runnable in-memory example.
auth = AuthKit(
    user_repo=my_user_repo,
    password_manager=my_password_manager,
    session_service=my_session_service,
    otp_store=my_otp_store,     # Optional: For MFA
    otp_manager=my_otp_manager  # Optional: For sending Emails/SMS
)

# 1. Register a user
user = auth.register.execute("alice@example.com", "secureRequest1!")

# 2. Login
session = auth.login.execute("alice@example.com", "secureRequest1!")
print(f"Access Token: {session.token}")
```

## 🛡️ Advanced Usage: OTP Flows

AuthKit supports secure, multi-step actions using OTPs (Time-based or Token-based).

### Delete Account with OTP
Securely delete an account by requiring verification.

```python
# 1. Start the deletion process (sends OTP to user's email/phone)
verification_token = auth.delete_account_otp_start.execute(user_id)

# 2. User enters the code they received
# 3. Verify and finalize deletion
auth.delete_account_otp_verify.execute(
    verification_token=verification_token, 
    code="123456"
)
```

## 📐 Architecture

AuthKit follows **Clean Architecture** principles:

*   **Core (`authkit.core`)**: Contains the `AuthKit` Facade, Registry, and Dependency Resolver.
*   **Ports (`authkit.ports`)**: Interfaces (Protocols) that your infrastructure must implement (e.g., `UserRepository`, `SessionService`).
*   **Use Cases (`authkit.usecases`)**: Pure business logic (e.g., `LoginUseCase`, `RegistrationUseCase`).
*   **Entities (`authkit.domain`)**: Data classes representing core concepts (`User`, `RegistrationIntent`).

### Dependency Injection
Dependencies are injected into the `AuthKit` constructor. You can provide a unified `user_repo` (for simple apps) or separate `user_reader` and `user_writer` (for CQRS/Scale).

## 🧩 Extending AuthKit

Want to add a "Greet User" feature?

### 1. Define the Use Case
```python
from authkit.core import Registry, UserRepository

@Registry.register("greet_user")
class GreetUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def execute(self, email: str):
        user = self.user_repo.get_by_identifier(email)
        print(f"Hello, {user.id}!")
```

### 2. (Optional) Typed Subclassing for IDE Support
To get full autocomplete in VS Code / PyCharm, define a typed subclass:

```python
from authkit import AuthKit

class MyAuthKit(AuthKit):
    greet_user: GreetUserUseCase

auth = MyAuthKit(...)
auth.greet_user.execute("alice@example.com") # IDE knows about this!
```

## 🏃 Running Examples

We provide runnable examples in the `examples/` directory.

- **[FastAPI + SQLModel + Redis](examples/fastapi_example/README.md)**: A complete reference implementation featuring:
  - MFA (Email/OTP) Login & Registration.
  - Secure Session Management (HttpOnly Cookies + Redis + SQL Persistence).
  - Swagger UI with Bearer Token integration.
  - CQRS Architecture (Separated Read/Write Repos).

## 🧪 Development

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Avneesh11905/AuthKit.git
    cd AuthKit
    ```

2.  **Install dependencies**:
    ```bash
    pip install .
    pip install mypy
    ```

3.  **Static Analysis**:
    ```bash
    mypy authkit/ examples/
    ```
