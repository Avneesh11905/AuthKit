# FastAPI + SQLModel + Redis Example

This example demonstrates how to integrate AuthKit with:
-   **FastAPI** for the API Layer.
-   **SQLModel** (SQLite) for User Persistence.
-   **Redis** for Session Management, OTPs, and Intent Storage.

## Prerequisites

1.  **Redis**: Ensure you have a Redis server running on `localhost:6379`.
2.  **Dependencies**: Install the required packages:
    ```bash
    pip install fastapi uvicorn sqlmodel redis
    ```

## Running the App

1.  Navigate to the `examples/fastapi_example` directory (or run from root):
    ```bash
    uvicorn examples.fastapi_example.main:app --reload
    ```
    *(Note: if running from root, ensure `AuthKit` is in your PYTHONPATH or installed in editable mode).*

2.  Open the Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Features

-   **Registration**:
    -   `POST /auth/register`: Direct registration (Email/Password).
    -   `POST /auth/register/start`: Sends an OTP (printed to console).
    -   `POST /auth/register/verify`: Verifies OTP and creates the user in `database.db`.
-   **Login (Separated Flows)**:
    -   `POST /auth/login`: Standard login (`email` + `password`) -> Returns Token & HttpOnly Cookie.
    -   `POST /auth/login/mfa/start`: Check creds & send OTP (First step of MFA). Returns `mfa_token`.
    -   `POST /auth/login/mfa/verify`: Verify (`mfa_token` + `otp`) -> Returns Token & HttpOnly Cookie.
-   **Token Refresh**:
    -   `POST /auth/refresh`: Reads `refresh_token` from HttpOnly Cookie. Rotates the session securely.
-   **Protected Route**:
    -   `GET /users/me`: Requires `Authorization: Bearer <token>`. Uses `HTTPBearer` in Swagger UI (Simple Paste).
