"""AI usage tracking and free-tier limit enforcement."""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import UsageRecord
from app.services.errors import UsageLimitReached
from app.services.subscription_service import get_current_subscription


def _current_period() -> str:
    now = datetime.now(timezone.utc)
    return f"{now.year:04d}-{now.month:02d}"


def _plan(db: Session, user_id: int) -> str:
    """Return the user's current plan, including expiration handling."""
    sub = get_current_subscription(db, user_id)
    return sub.plan


def get_usage(db: Session, user_id: int) -> dict:
    period = _current_period()

    # Get the current subscription once.
    sub = get_current_subscription(db, user_id)
    plan = sub.plan

    used = db.execute(
        select(func.count(UsageRecord.id)).where(
            UsageRecord.user_id == user_id,
            UsageRecord.period == period,
        )
    ).scalar_one()

    if plan == "plus":
        return {
            "plan": plan,
            "limit": None,
            "used": used,
            "remaining": None,
            "period": period,
            "reset_period": "monthly",
            "limit_reached": False,
            "expires_at": sub.expires_at,
        }

    limit = settings.FREE_MONTHLY_AI_SESSIONS
    remaining = max(0, limit - used)

    return {
        "plan": plan,
        "limit": limit,
        "used": used,
        "remaining": remaining,
        "period": period,
        "reset_period": "monthly",
        "limit_reached": remaining <= 0,
        "expires_at": None,
    }


def check_usage_limit(db: Session, user_id: int) -> dict:
    """Return usage; used by the check_usage_limit agent tool."""
    return get_usage(db, user_id)


def consume_session(db: Session, user_id: int) -> dict:
    """Record one AI session and enforce the free-tier limit."""

    usage = get_usage(db, user_id)

    if usage["limit_reached"]:
        raise UsageLimitReached(
            "You've reached your free Cartiva limit. "
            "Upgrade to Cartiva Plus for continued AI shopping."
        )

    db.add(
        UsageRecord(
            user_id=user_id,
            period=_current_period(),
        )
    )

    db.commit()

    return get_usage(db, user_id)