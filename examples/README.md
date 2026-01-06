# AuthKit Examples 🚀

This directory contains runnable examples demonstrating various ways to use **AuthKit**.

## 1. Quickstart (`quickstart.py`)
A complete, standalone demo using **In-Memory** adapters. It requires no external database.

**Features Demonstrated:**
*   Initializing `AuthKit` with simple adapters.
*   **Registration** and **Login** flows.
*   **Account Deletion with OTP**: Shows how to use the `configure()` method to inject new features (OTP) at runtime and execute a secure deletion flow.
*   Handling `User.last_login_at`.

```bash
# Run from project root
python examples/quickstart.py
```

## 2. Unit of Work Integration (`uow_demo.py`)
Demonstrates how to integrate AuthKit with a **Transactional Unit of Work** (simulating a SQL database session like SQLAlchemy).

**Key pattern:**
*   **Global Initialization**: Creating an empty `AuthKit` instance.
*   **Delayed Configuration**: Using `auth.configure(user_repo=...)` *inside* the transaction context to bind the repository to the current active session.

```bash
python examples/uow_demo.py
```

## 3. Extending AuthKit (`extensions_demo.py`)
Shows the **Extensibility** and **Type Safety** features.

**Features Demonstrated:**
*   **Custom Use Case**: Creating a `GreetUserUseCase` and registering it with `AuthKit`.
*   **Typed Facade**: Subclassing `AuthKit` to add type hints for your custom use cases (enabling IDE autocomplete).
*   **Custom Dependencies**: Injecting 3rd-party services (like a greeter class) into your use cases.

```bash
python examples/extensions_demo.py
```
