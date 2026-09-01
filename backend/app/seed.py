"""Seed the database with a demo customer and a realistic product catalog.

Run:  python -m app.seed

Products carry tags and related_ids so cross-sell, upsell and bundle logic work
against real relationships rather than hard-coded UI recommendations.
"""
from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.deps import DEMO_EMAIL
from app.models import Product, Subscription, User

# (name, description, category, price, image, stock, tags, related_names, is_premium)
PRODUCTS = [
    # ---- Fitness ----
    ("Gym Shoes", "Lightweight training shoes for everyday workouts.", "Fitness", 2999,
     "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600", 40,
     ["gym", "fitness", "workout", "shoes"], ["Gym Gloves", "Running Socks", "Premium Gym Shoes"], False),
    ("Premium Gym Shoes", "Cushioned pro training shoes with extra support.", "Fitness", 5499,
     "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?w=600", 20,
     ["gym", "fitness", "workout", "shoes", "premium"], ["Gym Gloves"], True),
    ("Gym Gloves", "Breathable gloves with padded grip.", "Fitness", 399,
     "https://images.unsplash.com/photo-1517963628607-235ccdd5476c?w=600", 100,
     ["gym", "fitness", "workout"], ["Gym Shoes", "Resistance Band"], False),
    ("Water Bottle", "Leak-proof 1L sports water bottle.", "Fitness", 499,
     "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600", 120,
     ["gym", "fitness", "travel", "hydration"], ["Gym Shoes", "Resistance Band"], False),
    ("Resistance Band", "Set of resistance bands for strength training.", "Fitness", 699,
     "https://images.unsplash.com/photo-1598289431512-b97b0917affc?w=600", 80,
     ["gym", "fitness", "workout"], ["Gym Gloves", "Yoga Mat"], False),
    ("Yoga Mat", "Non-slip cushioned yoga and exercise mat.", "Fitness", 999,
     "https://images.unsplash.com/photo-1592432678016-e910b452f9a2?w=600", 60,
     ["fitness", "yoga", "workout"], ["Resistance Band", "Water Bottle"], False),
    ("Running Shoes", "Responsive running shoes for road runs.", "Fitness", 3499,
     "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=600", 35,
     ["fitness", "running", "shoes"], ["Running Socks", "Water Bottle"], False),
    ("Running Socks", "Cushioned moisture-wicking running socks.", "Fitness", 299,
     "https://images.unsplash.com/photo-1586350977771-b3b0abd50c82?w=600", 200,
     ["fitness", "running"], ["Running Shoes"], False),

    # ---- Skincare ----
    ("Gentle Face Cleanser", "Daily foaming cleanser for all skin types.", "Skincare", 499,
     "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600", 90,
     ["skincare", "routine", "cleanser"], ["Vitamin C Serum", "Moisturizer"], False),
    ("Vitamin C Serum", "Brightening serum with antioxidants.", "Skincare", 899,
     "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600", 70,
     ["skincare", "routine", "serum"], ["Gentle Face Cleanser", "Moisturizer"], False),
    ("Moisturizer", "Lightweight hydrating daily moisturizer.", "Skincare", 599,
     "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=600", 110,
     ["skincare", "routine", "moisturizer"], ["Sunscreen SPF50", "Vitamin C Serum"], False),
    ("Sunscreen SPF50", "Broad-spectrum non-greasy sunscreen.", "Skincare", 549,
     "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=600", 95,
     ["skincare", "routine", "sunscreen"], ["Moisturizer"], False),
    ("Premium Retinol Serum", "Advanced anti-aging retinol treatment.", "Skincare", 1499,
     "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=600", 30,
     ["skincare", "serum", "premium"], ["Moisturizer"], True),

    # ---- Electronics ----
    ("Wireless Earbuds", "Compact earbuds with noise isolation.", "Electronics", 2499,
     "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600", 50,
     ["electronics", "tech", "audio"], ["Charging Cable", "Premium Wireless Earbuds"], False),
    ("Premium Wireless Earbuds", "ANC earbuds with premium sound.", "Electronics", 5999,
     "https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?w=600", 25,
     ["electronics", "tech", "audio", "premium"], ["Charging Cable"], True),
    ("Power Bank 10000mAh", "Fast-charging compact power bank.", "Electronics", 1299,
     "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=600", 80,
     ["electronics", "tech", "travel"], ["Charging Cable", "Wireless Earbuds"], False),
    ("Charging Cable", "Durable braided USB-C charging cable.", "Electronics", 299,
     "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600", 300,
     ["electronics", "tech"], ["Power Bank 10000mAh"], False),
    ("Bluetooth Speaker", "Portable speaker with deep bass.", "Electronics", 1999,
     "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=600", 45,
     ["electronics", "tech", "audio"], ["Charging Cable"], False),

    # ---- Fashion ----
    ("Cotton T-Shirt", "Soft breathable everyday cotton tee.", "Fashion", 799,
     "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600", 150,
     ["fashion", "casual"], ["Denim Jeans", "Canvas Sneakers"], False),
    ("Denim Jeans", "Slim-fit stretch denim jeans.", "Fashion", 1999,
     "https://images.unsplash.com/photo-1542272604-787c3835535d?w=600", 90,
     ["fashion", "casual"], ["Cotton T-Shirt", "Leather Belt"], False),
    ("Canvas Sneakers", "Classic low-top canvas sneakers.", "Fashion", 1799,
     "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=600", 70,
     ["fashion", "casual", "shoes"], ["Cotton T-Shirt"], False),
    ("Leather Belt", "Genuine leather belt with metal buckle.", "Fashion", 899,
     "https://images.unsplash.com/photo-1624222247344-550fb60583dc?w=600", 120,
     ["fashion", "accessory"], ["Denim Jeans"], False),

    # ---- Travel ----
    ("Cabin Backpack", "35L carry-on backpack with laptop sleeve.", "Travel", 2799,
     "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600", 55,
     ["travel", "bag"], ["Travel Organizer", "Neck Pillow", "Water Bottle"], False),
    ("Neck Pillow", "Memory-foam travel neck pillow.", "Travel", 699,
     "https://images.unsplash.com/photo-1520903920243-00d872a2d1c9?w=600", 100,
     ["travel", "comfort"], ["Cabin Backpack", "Eye Mask"], False),
    ("Travel Organizer", "Packing cubes and cable organizer set.", "Travel", 899,
     "https://images.unsplash.com/photo-1581553680321-4fffae59fccd?w=600", 85,
     ["travel", "organizer"], ["Cabin Backpack"], False),
    ("Eye Mask", "Contoured light-blocking sleep mask.", "Travel", 299,
     "https://images.unsplash.com/photo-1616627561950-9f746e330187?w=600", 140,
     ["travel", "comfort"], ["Neck Pillow"], False),
]


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Demo user + subscription
        user = db.execute(select(User).where(User.email == DEMO_EMAIL)).scalars().first()
        if not user:
            user = User(email=DEMO_EMAIL, name="Demo Customer")
            db.add(user)
            db.commit()
            db.refresh(user)
        if not db.execute(select(Subscription).where(Subscription.user_id == user.id)).scalars().first():
            db.add(Subscription(user_id=user.id, plan="free", status="active"))
            db.commit()

        # Products — idempotent per-product upsert keyed by unique name.
        # Insert only products that don't already exist, so running the seed
        # multiple times never creates duplicates and always fills any gaps.
        name_to_obj: dict[str, Product] = {}
        inserted = 0
        for (name, desc, cat, price, img, stock, tags, _rel, premium) in PRODUCTS:
            existing = db.execute(
                select(Product).where(Product.name == name)
            ).scalars().first()
            if existing:
                name_to_obj[name] = existing
                continue
            p = Product(
                name=name, description=desc, category=cat, price=price, image=img,
                stock=stock, tags=tags, related_ids=[], is_premium=premium,
            )
            db.add(p)
            name_to_obj[name] = p
            inserted += 1
        db.commit()

        # Resolve related_names -> related_ids now that all ids exist.
        for (name, _d, _c, _p, _i, _s, _t, rel_names, _pr) in PRODUCTS:
            obj = name_to_obj[name]
            resolved = [
                name_to_obj[r].id for r in rel_names if r in name_to_obj
            ]
            if obj.related_ids != resolved:
                obj.related_ids = resolved
        db.commit()

        total = db.execute(select(Product)).scalars().all()
        print(
            f"Seed complete. Inserted {inserted} new product(s); "
            f"catalog now has {len(total)} products."
        )
    finally:
        db.close()


if __name__ == "__main__":
    run()
