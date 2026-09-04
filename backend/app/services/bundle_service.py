"""Dynamic Bundle Builder.

Bundles are generated from the live catalog (never hard-coded). Given a goal
(e.g. "beginner gym kit") and an optional budget, it maps the goal to relevant
tags/category, selects a set of complementary products that fit the budget, and
explains the selection. It can also make an existing bundle cheaper.
"""

from sqlalchemy.orm import Session

from app.models import Product
from app.services.errors import BundleNotPossible
from app.services.product_service import search_products


# Lightweight goal → catalog mapping. Keeps intent parsing simple and
# deterministic for the MVP; the LLM layer can enrich this later.
GOAL_MAP: dict[str, dict] = {
    "makeup": {
        "category": None,
        "title": "Makeup Essentials",
        "tags": ["makeup"],
    },
    "skincare": {
        "category": "skincare",
        "title": "Skincare Essentials",
        "tags": ["skincare"],
    },
    "lipstick": {
        "category": "lipstick",
        "title": "Lipstick Collection",
        "tags": ["lipstick"],
    },
    "hair": {
        "category": "shampoo-and-conditioner",
        "title": "Hair Care Essentials",
        "tags": ["shampoo-and-conditioner"],
    },
    "shampoo": {
        "category": "shampoo-and-conditioner",
        "title": "Hair Care Essentials",
        "tags": ["shampoo-and-conditioner"],
    },
    "perfume": {
        "category": "perfume-and-body-mist",
        "title": "Fragrance Set",
        "tags": ["perfume-and-body-mist"],
    },
    "fragrance": {
        "category": "perfume-and-body-mist",
        "title": "Fragrance Set",
        "tags": ["perfume-and-body-mist"],
    },
    "tshirt": {
        "category": "tshirts",
        "title": "T-Shirt Collection",
        "tags": ["tshirts"],
    },
    "t-shirt": {
        "category": "tshirts",
        "title": "T-Shirt Collection",
        "tags": ["tshirts"],
    },
    "wallet": {
        "category": "wallets",
        "title": "Wallet Collection",
        "tags": ["wallets"],
    },
    "watch": {
        "category": "watches",
        "title": "Watch Collection",
        "tags": ["watches"],
    },
    "yoga": {
        "category": "yoga-mats",
        "title": "Yoga Essentials",
        "tags": ["yoga-mats"],
    },
    "mobile": {
        "category": "mobile-accessories",
        "title": "Mobile Accessories",
        "tags": ["mobile-accessories"],
    },
}


def _resolve_goal(goal: str) -> dict:
    g = goal.lower()

    for keyword, cfg in GOAL_MAP.items():
        if keyword in g:
            return cfg

    # Fallback: treat the goal text as a free search with a generic title.
    return {
        "category": None,
        "title": "Custom Bundle",
        "tags": [],
        "query": goal,
    }


def _select_within_budget(
    candidates: list[Product],
    budget: float | None,
    max_items: int = 5,
) -> list[Product]:
    """Greedy selection favouring variety: pick complementary items
    (cheapest first) until the budget is spent or we hit max_items.
    """

    chosen: list[Product] = []
    total = 0.0

    # Cheapest-first keeps the bundle affordable and lets more items fit.
    for product in sorted(candidates, key=lambda p: p.price):
        if product.stock <= 0:
            continue

        if budget is not None and total + product.price > budget:
            continue

        chosen.append(product)
        total += product.price

        if len(chosen) >= max_items:
            break

    return chosen


def build_bundle(
    db: Session,
    goal: str,
    budget: float | None = None,
) -> dict:
    cfg = _resolve_goal(goal)

    candidates = search_products(
        db,
        query=cfg.get("query"),
        category=cfg.get("category"),
        tags=cfg.get("tags") or None,
        limit=50,
    )

    # Broaden the search if the tag/category filter was too narrow.
    if len(candidates) < 2 and cfg.get("category"):
        candidates = search_products(
            db,
            category=cfg["category"],
            limit=50,
        )

    chosen = _select_within_budget(
        candidates,
        budget,
    )

    if len(chosen) < 2:
        raise BundleNotPossible(
            "I couldn't build a bundle that fits within that budget. "
            "Try increasing the budget or changing the goal."
        )

    total = round(
        sum(p.price for p in chosen),
        2,
    )

    within = budget is None or total <= budget

    names = ", ".join(
        p.name for p in chosen
    )

    explanation = (
        f"I picked {len(chosen)} complementary products "
        f"({names}) that work well together for your goal"
        + (
            f" and stay within ₹{int(budget)}."
            if budget
            else "."
        )
    )

    return {
        "title": cfg["title"],
        "items": [{"product": p} for p in chosen],
        "total": total,
        "budget": budget,
        "within_budget": within,
        "explanation": explanation,
    }


def make_cheaper(
    db: Session,
    goal: str,
    current_total: float,
) -> dict:
    """Rebuild the bundle with a lower budget target (~85% of current)."""

    target = round(
        current_total * 0.85,
        2,
    )

    return build_bundle(
        db,
        goal,
        budget=target,
    )