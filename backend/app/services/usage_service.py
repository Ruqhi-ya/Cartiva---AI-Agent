"""AI usage tracking and free-tier limit enforcement.

The limit is read from configuration (settings.FREE_MONTHLY_AI_SESSIONS) and
the reset period is monthly. Cartiva Plus users are treated as unlimited.
"""
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Subscription, UsageRecord
from app.services.errors import UsageLimitReached


def _current_period() -> str:
    now = datetime.now(timezone.utc)
    return f"{now.year:04d}-{now.month:02d}"


def _plan(db: Session, user_id: int) -> str:
    sub = db.execute(
        select(Subscription).where(Subscription.user_id == user_id)
    ).scalars().first()
    return sub.plan if sub else "free"


def get_usage(db: Session, user_id: int) -> dict:
    period = _current_period()
    plan = _plan(db, user_id)

    used = db.execute(
        select(func.count(UsageRecord.id)).where(
            UsageRecord.user_id == user_id, UsageRecord.period == period
        )
    ).scalar_one()

    if plan == "plus":
        # Plus is treated as unlimited in the MVP
        return {
            "plan": plan,
            "limit": None,
            "used": used,
            "remaining": None,
            "period": period,
            "reset_period": "monthly",
            "limit_reached": False,
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
    }


def check_usage_limit(db: Session, user_id: int) -> dict:
    """Return usage; used by the check_usage_limit agent tool (read-only)."""
    return get_usage(db, user_id)


def consume_session(db: Session, user_id: int) -> dict:
    """Record one AI session. Raises UsageLimitReached for free users at the cap."""
    usage = get_usage(db, user_id)
    if usage["limit_reached"]:
        raise UsageLimitReached(
            "You've reached your free Cartiva limit. Upgrade to Cartiva Plus for "
            "continued AI shopping."
        )
    db.add(UsageRecord(user_id=user_id, period=_current_period()))
    db.commit()
    return get_usage(db, user_id)
