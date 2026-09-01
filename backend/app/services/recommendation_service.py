"""Smart Cart Optimizer: cross-sell and upsell recommendations.

Recommendations are derived from real product relationships (related_ids and
tag overlap) rather than random ads, so they stay relevant. The AI never adds
these automatically — the customer must approve each one.
"""
from sqlalchemy.orm import Session

from app.models import Cart, Product
from app.services.product_service import find_related, get_product


def _cross_sell_reason(base: Product, rec: Product) -> str:
    return f"Commonly bought with {base.name}."


def _upsell_reason(base: Product, rec: Product) -> str:
    return f"A premium alternative to {base.name} with better features."


def recommend_for_product(db: Session, product_id: int, limit: int = 4) -> list[dict]:
    base = get_product(db, product_id)
    related = find_related(db, product_id, limit=limit * 2)

    recs: list[dict] = []
    for rec in related:
        # Upsell: same category, premium, and more expensive than the base item.
        if rec.category == base.category and rec.is_premium and rec.price > base.price:
            recs.append(
                {"product": rec, "reason": _upsell_reason(base, rec), "kind": "upsell"}
            )
        else:
            recs.append(
                {
                    "product": rec,
                    "reason": _cross_sell_reason(base, rec),
                    "kind": "cross_sell",
                }
            )
        if len(recs) >= limit:
            break
    return recs


def recommend_for_cart(db: Session, cart: Cart, limit: int = 4) -> list[dict]:
    """Analyze the whole cart and suggest complementary/premium products not
    already in it."""
    in_cart = {item.product_id for item in cart.items}
    recs: list[dict] = []
    seen: set[int] = set(in_cart)

    for item in cart.items:
        for rec in recommend_for_product(db, item.product_id, limit=limit):
            pid = rec["product"].id
            if pid not in seen:
                recs.append(rec)
                seen.add(pid)
            if len(recs) >= limit:
                return recs
    return recs
