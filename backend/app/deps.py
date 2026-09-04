"""Authentication dependencies for Cartiva."""

from fastapi import Cookie, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.services.auth_token_service import verify_access_token


def get_current_user_id(
    db: Session = Depends(get_db),
    cartiva_token: str | None = Cookie(default=None),
) -> int:
    """Return the authenticated customer's user ID."""

    if not cartiva_token:
        raise HTTPException(
            status_code=401,
            detail="Please log in to use Cartiva.",
        )

    user_id = verify_access_token(cartiva_token)

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Your session has expired. Please log in again.",
        )

    user = db.execute(
        select(User).where(User.id == user_id)
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User account not found.",
        )

    return user.id