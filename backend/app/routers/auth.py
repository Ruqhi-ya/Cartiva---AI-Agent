"""Cartiva customer authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User
from app.schemas import AuthResponse, LoginRequest, SignupRequest
from app.services.auth_service import hash_password, verify_password
from app.services.auth_token_service import create_access_token


router = APIRouter(prefix="/api/auth", tags=["auth"])


def _set_auth_cookie(response: Response, user_id: int) -> None:
    """Store the JWT in a secure HttpOnly cookie."""
    token = create_access_token(user_id)

    response.set_cookie(
        key="cartiva_token",
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="none",
        max_age=7 * 24 * 60 * 60,
    )


@router.post("/signup", response_model=AuthResponse)
def signup(
    payload: SignupRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    email = payload.email.strip().lower()
    name = payload.name.strip()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Name is required.",
        )

    if len(payload.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters.",
        )

    existing_user = db.execute(
        select(User).where(User.email == email)
    ).scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="An account with this email already exists.",
        )

    user = User(
        name=name,
        email=email,
        password_hash=hash_password(payload.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    _set_auth_cookie(response, user.id)

    return AuthResponse(
        message="Account created successfully.",
        user_id=user.id,
        name=user.name,
        email=user.email,
    )


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    email = payload.email.strip().lower()

    user = db.execute(
        select(User).where(User.email == email)
    ).scalars().first()

    if (
        not user
        or not user.password_hash
        or not verify_password(
            payload.password,
            user.password_hash,
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    _set_auth_cookie(response, user.id)

    return AuthResponse(
        message="Login successful.",
        user_id=user.id,
        name=user.name,
        email=user.email,
    )


@router.post("/logout")
def logout(response: Response):
    """Log the customer out by removing the authentication cookie."""
    response.delete_cookie(
        key="cartiva_token",
    )

    return {
        "message": "Logged out successfully.",
    }