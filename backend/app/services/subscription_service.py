"""Subscription state management.

Real billing (Razorpay Test Mode) is intentionally NOT integrated yet. The
`provider` / `provider_subscription_id` fields and this service form the clean
integration point for a later task.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Subscription


def get_or_create_subscription(db: Session, user_id: int) -> Subscription:
    sub = db.execute(
        select(Subscription).where(Subscription.user_id == user_id)
    ).scalars().first()
    if not sub:
        sub = Subscription(user_id=user_id, plan="free", status="active")
        db.add(sub)
        db.commit()
        db.refresh(sub)
    return sub


def set_plan(db: Session, user_id: int, plan: str) -> Subscription:
    """Switch plan. In this MVP no payment occurs — this simulates the state
    change that Razorpay would trigger via webhook later."""
    sub = get_or_create_subscription(db, user_id)
    sub.plan = plan
    sub.status = "active"
    db.commit()
    db.refresh(sub)
    return sub
