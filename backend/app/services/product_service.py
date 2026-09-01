"""Product catalog access: search, retrieval and relationship lookups."""
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Product
from app.services.errors import ProductNotFound


def list_categories(db: Session) -> list[str]:
    rows = db.execute(select(Product.category).distinct()).scalars().all()
    return sorted(rows)


def search_products(
    db: Session,
    query: str | None = None,
    category: str | None = None,
    max_price: float | None = None,
    tags: list[str] | None = None,
    limit: int = 50,
) -> list[Product]:
    stmt = select(Product)
    if query:
        like = f"%{query.lower()}%"
        stmt = stmt.where(
            or_(
                Product.name.ilike(like),
                Product.description.ilike(like),
            )
        )
    if category:
        stmt = stmt.where(Product.category.ilike(category))
    if max_price is not None:
        stmt = stmt.where(Product.price <= max_price)

    products = list(db.execute(stmt.limit(limit)).scalars().all())

    # Tag filtering done in Python since tags are stored as JSON.
    if tags:
        wanted = {t.lower() for t in tags}
        products = [
            p for p in products if wanted & {str(t).lower() for t in (p.tags or [])}
        ]
    return products


def get_product(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if not product:
        raise ProductNotFound(f"We couldn't find that product.")
    return product


def find_related(db: Session, product_id: int, limit: int = 6) -> list[Product]:
    """Return related products using explicit related_ids first, then tag overlap."""
    product = get_product(db, product_id)
    results: list[Product] = []
    seen: set[int] = {product.id}

    # 1) Explicit relationships
    for rid in product.related_ids or []:
        related = db.get(Product, rid)
        if related and related.id not in seen and related.stock > 0:
            results.append(related)
            seen.add(related.id)

    # 2) Tag overlap within reason
    if len(results) < limit and product.tags:
        candidates = search_products(db, tags=product.tags, limit=50)
        for c in candidates:
            if c.id not in seen and c.stock > 0:
                results.append(c)
                seen.add(c.id)
            if len(results) >= limit:
                break

    return results[:limit]
