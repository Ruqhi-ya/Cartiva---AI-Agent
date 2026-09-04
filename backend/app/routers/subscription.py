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
    VerifyPaymentRequest,
)
from app.services import subscription_service


router = APIRouter(
    prefix="/api/subscription",
    tags=["subscription"],
)


def _razorpay_client():
    """Create a Razorpay client using configured credentials."""
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
def get_subscription(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Get the current user's Cartiva Plus subscription."""
    subscription = subscription_service.get_current_subscription(
        db,
        user_id,
    )

    return SubscriptionOut(
        plan=subscription.plan,
        status=subscription.status,
        started_at=subscription.started_at,
        expires_at=subscription.expires_at,
    )


@router.post("/create-order", response_model=CreateOrderOut)
def create_order(
    user_id: int = Depends(get_current_user_id),
):
    """Create a Razorpay Test Mode order for Cartiva Plus."""

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
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to create Razorpay order.",
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
    user_id: int = Depends(get_current_user_id),
):
    """Verify Razorpay payment and activate Cartiva Plus."""

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
        started_at=subscription.started_at,
        expires_at=subscription.expires_at,
    )