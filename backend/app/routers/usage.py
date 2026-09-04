"""Usage + subscription endpoints."""

from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user_id
from app.schemas import SubscriptionOut, UpgradeRequest, UsageOut
from app.services import subscription_service, usage_service


router = APIRouter(prefix="/api", tags=["usage"])


@router.get("/usage", response_model=UsageOut)
def get_usage(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return usage_service.get_usage(db, user_id)


@router.get("/subscription", response_model=SubscriptionOut)
def get_subscription(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    sub = subscription_service.get_current_subscription(db, user_id)

    return SubscriptionOut(
        plan=sub.plan,
        status=sub.status,
        started_at=sub.started_at,
        expires_at=sub.expires_at,
    )


@router.post("/subscription/upgrade", response_model=SubscriptionOut)
def upgrade(
    payload: UpgradeRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Legacy/dev endpoint for manually changing the plan."""

    sub = subscription_service.set_plan(
        db,
        user_id,
        payload.plan,
    )

    return SubscriptionOut(
        plan=sub.plan,
        status=sub.status,
        started_at=sub.started_at,
        expires_at=sub.expires_at,
    )