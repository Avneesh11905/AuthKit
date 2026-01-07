from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Response, Cookie
from authkit import AuthKit, User

from .database import create_db_and_tables
from .models import (
    RegisterRequest,
    RegisterStartRequest, 
    RegisterVerifyRequest, 
    LoginRequest, 
    RecoverStartRequest, 
    RecoverVerifyRequest, 
    UserResponse
)
from .dependencies import get_authkit, get_current_user
from fastapi import status

# --- Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan, title="AuthKit + SQLModel + Redis Example")

# --- Routes ---

@app.post("/auth/register")
def register(
    request: RegisterRequest,
    auth: Annotated[AuthKit, Depends(get_authkit)]
):
    try:
        # Use Case: Direct Registration
        user = auth.register.execute(identifier=request.email, password=request.password)
        return {"message": "User registered successfully", "user_id": user.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/register/start")
def register_start(
    request: RegisterStartRequest,
    auth: Annotated[AuthKit, Depends(get_authkit)]
):
    try:
        token = auth.register_otp_start.execute(identifier=request.email, password=request.password)
        return {"message": "OTP sent to console", "token": token}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/register/verify")
def register_verify(
    request: RegisterVerifyRequest,
    auth: Annotated[AuthKit, Depends(get_authkit)]
):
    try:
        user = auth.register_otp_verify.execute(verification_token=request.token, code=request.otp)
        return {"message": "User registered successfully", "user_id": user.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

from .dependencies import get_authkit, get_current_user
from fastapi import status

def set_refresh_cookie(response: Response, token: str):
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        secure=False, 
        samesite="lax",
        max_age=7 * 24 * 60 * 60
    )

@app.post("/auth/login")
def login(
    response: Response,
    request: LoginRequest,
    auth: Annotated[AuthKit, Depends(get_authkit)]
):
    try:
        # Standard Password Login
        session = auth.login.execute(identifier=request.email, password=request.password)
             
        # Success - Set Cookie & Return Token
        if getattr(session, "refresh_token", None):
            set_refresh_cookie(response, session.refresh_token)
        
        return {
            "access_token": session.token, 
            "token_type": "bearer"
        }

    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

from .models import MFAVerifyRequest
@app.post("/auth/login/mfa/start")
def login_mfa_start(
    request: LoginRequest,
    auth: Annotated[AuthKit, Depends(get_authkit)]
):
    try:
        # Uses 'login_otp_start' use case
        token = auth.login_otp_start.execute(identifier=request.email, password=request.password)
        return {"message": "MFA OTP sent to console", "mfa_token": token}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/auth/login/mfa/verify")
def login_mfa_verify(
    response: Response,
    request: MFAVerifyRequest,
    auth: Annotated[AuthKit, Depends(get_authkit)]
):
    try:
        session = auth.login_otp_verify.execute(verification_token=request.token, code=request.otp)
        if getattr(session, "refresh_token", None):
            set_refresh_cookie(response, session.refresh_token)
        
        return {
            "access_token": session.token, 
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/auth/refresh")
def refresh_token(
    response: Response,
    auth: Annotated[AuthKit, Depends(get_authkit)],
    refresh_token: Annotated[str | None, Cookie()] = None,
):
    try:
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Refresh token missing")
            
        new_session = auth._adapters.session_service.refresh(refresh_token)
        if not new_session:
             raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
        
        # Rotate Refresh Token Cookie
        set_refresh_cookie(response, new_session.refresh_token)
             
        return {
            "access_token": new_session.token, 
            "token_type": "bearer"
        }
    except Exception as e:
         raise HTTPException(status_code=401, detail=str(e))

@app.post("/auth/recover/start")
def recover_start(
    request: RecoverStartRequest,
    auth: Annotated[AuthKit, Depends(get_authkit)]
):
    try:
        # "forget_password_start"
        token = auth.forget_password_start.execute(identifier=request.email)
        return {"message": "Recovery OTP sent to console", "token": token}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/recover/verify")
def recover_verify(
    request: RecoverVerifyRequest,
    auth: Annotated[AuthKit, Depends(get_authkit)]
):
    try:
        # "forget_password_verify"
        auth.forget_password_verify.execute(
            token=request.token, 
            code=request.otp, 
            new_password=request.new_password
        )
        return {"message": "Password updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/me", response_model=UserResponse)
def get_me(
    user: Annotated[User, Depends(get_current_user)]
):
    return UserResponse(
        id=user.id,
        email=user.identifier,
        active=True 
    )
