# AuthKit

A robust, Clean Architecture-based authentication library for Python. AuthKit is designed to be framework-agnostic, easily extensible, and highly testable, providing a solid foundation for implementing secure authentication flows in any Python application.

## Features

- **Architectural Excellence**:
    - **Clean Architecture**: Domain-centric design with strict dependency rules.
    - **Flexible Persistence**: Choose between **Unified Repository** (Simpler) or **CQRS** (Scalable) patterns depending on your needs.
    - **Technology Independent**: Framework-agnostic core (use with FastAPI, Flask, Django, etc.) and database-agnostic persistence (SQL, NoSQL, In-Memory).
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

## Quick Start

The fastest way to understand AuthKit is to run the self-contained example. It implements standard "Zero-Dependency" in-memory adapters to demonstrate the full Registration flow.

**[View the Quick Start Script](examples/quickstart.py)**

To run it:
```bash
python examples/quickstart.py
```

## Integrating into Your Project

To use AuthKit in production, you must implement the Core Ports (Interfaces) using your technology stack (e.g., SQLAlchemy, Redis, Argon2).

### 1. Implement Core Ports

You can choose between a **Unified** approach (Simpler) or **CQRS** (Advanced).

**Option A: Unified Repository (Recommended for most apps)**
Implement `UserRepository` which combines read and write operations.

| Interface | Responsibility | Example Implementation |
|-----------|----------------|------------------------|
| `UserRepository` | Handles all user persistence (Read & Write). | `Select/Add/Update(User)` |
| `PasswordManager` | Hashing and verification logic. | `passlib` or `argon2-cffi` wrapper. |
| `TokenService` | Token generation and validation. | `PyJWT` wrapper for HS256/RS256. |

**Option B: CQRS (For high scalability)**
Implement separate `UserReaderRepository` and `UserWriterRepository` interfaces if you need to split read/write models.

### 2. Dependency Injection

Inject your production adapters into the Use Cases:

```python
# Setup your adapters
user_repo = PostgresUserRepo() # Implements UserRepository
password_manager = Argon2PasswordManager()
token_service = JwtTokenService()

# Initialize Use Case
# Note: For Unified Repos, inject the SAME instance for both reader and writer
login_uc = LoginCQRSUseCase(
    user_reader=user_repo,
    user_writer=user_repo,
    password_manager=password_manager,
    token_service=token_service
)

# Execute
token = await login_uc.execute("user@example.com", "password")
```

## Testing

The project includes a comprehensive test suite using `pytest`.

To run the tests:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
# Run tests
pytest
```

### Testing Strategy

The tests are designed to be **Expectation-Based** and **Isolated**:
- **Expectation-Based**: Tests verify the behavioral contract of the Use Cases (Inputs -> Outputs/Side Effects) rather than internal implementation details.
- **Dependency Injection**: We use `Fake` implementations of ports (Repositories, Stores) injected into the Use Cases.
- **Isolation**: Each test runs with a fresh, isolated state (new in-memory stores) to prevent leakage and ensure reliability.


## License

[MIT](LICENSE)
