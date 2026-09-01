"""Shared dependencies.

For the MVP we use a single seeded demo customer. The dependency is isolated
here so real authentication can be dropped in later without touching routers.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User

DEMO_EMAIL = "demo@cartiva.app"


def get_current_user_id(db: Session) -> int:
    user = db.execute(select(User).where(User.email == DEMO_EMAIL)).scalars().first()
    if not user:
        # Auto-provision the demo user if seed hasn't run.
        user = User(email=DEMO_EMAIL, name="Demo Customer")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user.id
