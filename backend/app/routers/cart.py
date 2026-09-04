"""Cart endpoints. Totals are computed server-side; frontend prices are ignored."""

from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user_id
from app.schemas import AddToCartRequest, CartOut
from app.services import cart_service


router = APIRouter(prefix="/api/cart", tags=["cart"])


def _cart_out(db: Session, user_id: int) -> dict:
    cart = cart_service.get_or_create_cart(db, user_id)
    return cart_service.serialize_cart(db, cart)


@router.get("", response_model=CartOut)
def get_cart(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return _cart_out(db, user_id)


@router.post("/items", response_model=CartOut)
def add_item(
    payload: AddToCartRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    cart = cart_service.add_item(
        db,
        user_id,
        payload.product_id,
        payload.quantity,
    )
    return cart_service.serialize_cart(db, cart)


@router.delete("/items/{item_id}", response_model=CartOut)
def remove_item(
    item_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    cart = cart_service.remove_item(db, user_id, item_id)
    return cart_service.serialize_cart(db, cart)