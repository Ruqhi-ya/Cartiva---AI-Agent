"""Cartiva Plus subscription and Razorpay payment endpoints."""

import razorpay

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.deps import get_current_user_id
from app.schemas import (
    CreateOrderOut,
    SubscriptionOut,
    UpgradeRequest,
    VerifyPaymentRequest,
)
from app.services import subscription_service


router = APIRouter(
    prefix="/api/subscription",
    tags=["subscription"],
)


def _razorpay_client():
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Razorpay is not configured.",
        )

    return razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET,
        )
    )


@router.get("", response_model=SubscriptionOut)
def get_subscription(db: Session = Depends(get_db)):
    user_id = get_current_user_id(db)

    subscription = subscription_service.get_or_create_subscription(
        db,
        user_id,
    )

    return SubscriptionOut(
        plan=subscription.plan,
        status=subscription.status,
    )


@router.post("/upgrade", response_model=SubscriptionOut)
def upgrade(
    payload: UpgradeRequest,
    db: Session = Depends(get_db),
):
    """Legacy/dev endpoint for manually changing the plan."""

    user_id = get_current_user_id(db)

    subscription = subscription_service.set_plan(
        db,
        user_id,
        payload.plan,
    )

    return SubscriptionOut(
        plan=subscription.plan,
        status=subscription.status,
    )


@router.post("/create-order", response_model=CreateOrderOut)
def create_order(db: Session = Depends(get_db)):
    """Create a Razorpay Test Mode order for Cartiva Plus."""

    user_id = get_current_user_id(db)

    client = _razorpay_client()

    # Cartiva Plus = ₹499/month.
    # Razorpay expects the amount in paise.
    amount = 49900

    try:
        order = client.order.create(
            data={
                "amount": amount,
                "currency": "INR",
                "receipt": f"cartiva_plus_{user_id}",
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to create Razorpay order: {str(e)}",
        )

    return CreateOrderOut(
        order_id=order["id"],
        amount=amount,
        currency="INR",
        key_id=settings.RAZORPAY_KEY_ID,
    )


@router.post("/verify-payment", response_model=SubscriptionOut)
def verify_payment(
    payload: VerifyPaymentRequest,
    db: Session = Depends(get_db),
):
    """Verify Razorpay payment and activate Cartiva Plus."""

    user_id = get_current_user_id(db)

    client = _razorpay_client()

    try:
        client.utility.verify_payment_signature(
            {
                "razorpay_order_id": payload.razorpay_order_id,
                "razorpay_payment_id": payload.razorpay_payment_id,
                "razorpay_signature": payload.razorpay_signature,
            }
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Payment verification failed.",
        )

    # Signature is valid, so activate Plus.
    subscription = subscription_service.set_plan(
        db,
        user_id,
        "plus",
    )

    return SubscriptionOut(
        plan=subscription.plan,
        status=subscription.status,
    )