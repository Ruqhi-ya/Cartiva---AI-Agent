"""Usage + subscription endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user_id
from app.schemas import SubscriptionOut, UpgradeRequest, UsageOut
from app.services import subscription_service, usage_service

router = APIRouter(prefix="/api", tags=["usage"])


@router.get("/usage", response_model=UsageOut)
def get_usage(db: Session = Depends(get_db)):
    user_id = get_current_user_id(db)
    return usage_service.get_usage(db, user_id)


@router.get("/subscription", response_model=SubscriptionOut)
def get_subscription(db: Session = Depends(get_db)):
    user_id = get_current_user_id(db)
    sub = subscription_service.get_or_create_subscription(db, user_id)
    return SubscriptionOut(plan=sub.plan, status=sub.status)


@router.post("/subscription/upgrade", response_model=SubscriptionOut)
def upgrade(payload: UpgradeRequest, db: Session = Depends(get_db)):
    """Switch plan. No real billing yet — this is the integration point for
    Razorpay Test Mode in a later task."""
    user_id = get_current_user_id(db)
    sub = subscription_service.set_plan(db, user_id, payload.plan)
    return SubscriptionOut(plan=sub.plan, status=sub.status)
