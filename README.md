# AuthKit

A robust, Clean Architecture-based authentication library for Python. AuthKit is designed to be framework-agnostic, easily extensible, and highly testable, providing a solid foundation for implementing secure authentication flows in any Python application.

## Features

- **Clean Architecture Design**: Distinct separation of concerns with `Use Cases`, `Domain` entities, and `Ports` (interfaces).
- **Core Authentication**:
    - User Registration
    - Login (Username/Password)
    - Logout (Single session)
    - Logout All (Global session revocation)
- **Credential Management**:
    - Change Password (with automatic session revocation)
    - Forget Password Flows (OTP based)
- **Multi-Factor Authentication (MFA)**:
    - Login with OTP support
- **Extensible Ports**:
    - `UserRepository`: For user persistence.
    - `PasswordManager`: For hashing and verification.
    - `TokenService`: For token generation and management.
    - `OTPStore` & `OTPManager`: For handling One-Time Passwords.
- **Type Safe**: Comprehensive Python type hints.

## Directory Structure

```
authkit/
├── domain/       # Core entities (User, RegistrationIntent) and Enums
├── ports/        # Protocols (Interfaces) for external dependencies
├── usecases/     # Business logic implementations
│   ├── Account/
│   ├── Authentication/
│   └── Credential/
└── exceptions/   # Domain-specific errors
```

## Installation

Ensure you have Python 3.10+ installed.

You can install the package locally:

```bash
pip install .
```

## Usage

AuthKit relies on Dependency Injection. You must implement the interfaces defined in `authkit.ports` (Adapters) and inject them into the Use Cases.

### 1. Implement Ports

Create adapters for your specific infrastructure (e.g., SQLalchemy, Redis, JWT, Argon2).

```python
# Example Adapters (Not included in library)
class PostgresRepo(UserRepository):
    ...

class JWTService(TokenService):
    ...
```

### 2. Initialize Use Case

```python
import asyncio
from authkit.usecases import LoginUseCase

async def main():
    # Setup dependencies
    user_repo = PostgresRepo(...)
    token_service = JWTService(...)
    password_manager = Argon2Manager(...)

    # Initialize Use Case
    login_uc = LoginUseCase(user_repo, password_manager, token_service)

    # Execute
    try:
        token = await login_uc.execute("user@example.com", "securePassword123!")
        print(f"Login successful! Token: {token.token}")
    except Exception as e:
        print(f"Login failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Testing

The project includes a comprehensive test suite using `pytest`.

To run the tests:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

## License

[MIT](LICENSE)
