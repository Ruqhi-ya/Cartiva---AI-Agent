"""Subscription lifecycle management for Cartiva."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Subscription


# Temporary duration for testing.
# Change to 3 days later, and eventually use Razorpay's
# real subscription billing period in production.
PLUS_DURATION_DAYS = 3


def _now() -> datetime:
    return datetime.now(timezone.utc)


def get_or_create_subscription(
    db: Session,
    user_id: int,
) -> Subscription:
    sub = db.execute(
        select(Subscription).where(
            Subscription.user_id == user_id
        )
    ).scalars().first()

    if not sub:
        sub = Subscription(
            user_id=user_id,
            plan="free",
            status="active",
            provider="",
            provider_subscription_id="",
            started_at=None,
            expires_at=None,
        )

        db.add(sub)
        db.commit()
        db.refresh(sub)

    return sub


def expire_if_needed(
    db: Session,
    sub: Subscription,
) -> Subscription:
    """Downgrade an expired Plus subscription to Free."""

    if (
        sub.plan == "plus"
        and sub.expires_at is not None
        and sub.expires_at <= _now()
    ):
        sub.plan = "free"
        sub.status = "expired"

        db.commit()
        db.refresh(sub)

    return sub


def get_current_subscription(
    db: Session,
    user_id: int,
) -> Subscription:
    """Return the user's subscription after checking expiration."""

    sub = get_or_create_subscription(db, user_id)

    return expire_if_needed(db, sub)


def set_plan(
    db: Session,
    user_id: int,
    plan: str,
) -> Subscription:
    """Change the user's plan.

    This is still using a temporary local expiration period.
    Razorpay subscription/webhook integration will later become
    the source of truth for real billing.
    """

    if plan not in {"free", "plus"}:
        raise ValueError("Invalid subscription plan.")

    sub = get_or_create_subscription(db, user_id)

    if plan == "plus":
        now = _now()

        sub.plan = "plus"
        sub.status = "active"
        sub.started_at = now
        sub.expires_at = now + timedelta(
            days=PLUS_DURATION_DAYS
        )

    else:
        sub.plan = "free"
        sub.status = "active"
        sub.started_at = None
        sub.expires_at = None

    db.commit()
    db.refresh(sub)

    return sub