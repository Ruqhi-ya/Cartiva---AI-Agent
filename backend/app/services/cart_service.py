"""Cart operations. Totals are always calculated on the backend — prices from
the frontend are never trusted."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Cart, CartItem, Product
from app.services.errors import InsufficientStock, ProductNotFound
from app.services.product_service import get_product


def get_or_create_cart(db: Session, user_id: int) -> Cart:
    cart = db.execute(
        select(Cart).where(Cart.user_id == user_id).order_by(Cart.id.desc())
    ).scalars().first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def add_item(db: Session, user_id: int, product_id: int, quantity: int = 1) -> Cart:
    cart = get_or_create_cart(db, user_id)
    product = get_product(db, product_id)  # validates existence

    if product.stock < quantity:
        raise InsufficientStock(f"Only {product.stock} of {product.name} left in stock.")

    item = db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id, CartItem.product_id == product_id
        )
    ).scalars().first()

    if item:
        if product.stock < item.quantity + quantity:
            raise InsufficientStock(
                f"Only {product.stock} of {product.name} left in stock."
            )
        item.quantity += quantity
    else:
        db.add(CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity))

    db.commit()
    db.refresh(cart)
    return cart


def remove_item(db: Session, user_id: int, item_id: int) -> Cart:
    cart = get_or_create_cart(db, user_id)
    item = db.get(CartItem, item_id)
    # Ensure the item belongs to this user's cart (prevent unauthorized changes)
    if not item or item.cart_id != cart.id:
        raise ProductNotFound("That item isn't in your cart.")
    db.delete(item)
    db.commit()
    db.refresh(cart)
    return cart


def calculate_total(db: Session, cart: Cart) -> dict:
    """Compute subtotal/total server-side from live product prices."""
    subtotal = 0.0
    count = 0
    for item in cart.items:
        price = item.product.price if item.product else 0.0
        subtotal += price * item.quantity
        count += item.quantity
    # MVP: total == subtotal (no shipping/tax logic yet)
    return {"subtotal": round(subtotal, 2), "total": round(subtotal, 2), "item_count": count}


def serialize_cart(db: Session, cart: Cart) -> dict:
    totals = calculate_total(db, cart)
    items = []
    for item in cart.items:
        price = item.product.price if item.product else 0.0
        items.append(
            {
                "id": item.id,
                "product": item.product,
                "quantity": item.quantity,
                "line_total": round(price * item.quantity, 2),
            }
        )
    return {
        "id": cart.id,
        "items": items,
        "subtotal": totals["subtotal"],
        "total": totals["total"],
        "item_count": totals["item_count"],
    }
