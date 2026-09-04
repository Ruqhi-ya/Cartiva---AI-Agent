"""JWT token helpers for Cartiva authentication."""

from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings


# JWT secret comes from the application's environment configuration.
# It must be configured in .env locally and as an environment variable
# in production.
SECRET_KEY = settings.CARTIVA_JWT_SECRET

if not SECRET_KEY:
    raise RuntimeError(
        "CARTIVA_JWT_SECRET environment variable is not configured."
    )


ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = 7


def create_access_token(user_id: int) -> str:
    """Create a JWT token for an authenticated user."""
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(days=TOKEN_EXPIRE_DAYS),
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return token


def verify_access_token(token: str) -> int | None:
    """Verify a JWT token and return the user ID."""
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if not user_id:
            return None

        return int(user_id)

    except (jwt.InvalidTokenError, ValueError, TypeError):
        return None