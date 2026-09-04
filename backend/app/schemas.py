"""Pydantic request/response schemas with validation."""
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from datetime import datetime

# ---------- Products ----------
class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    category: str
    price: float
    image: str
    stock: int
    tags: list[str]
    is_premium: bool


# ---------- Cart ----------
class CartItemOut(BaseModel):
    id: int
    product: ProductOut
    quantity: int
    line_total: float


class CartOut(BaseModel):
    id: int
    items: list[CartItemOut]
    subtotal: float
    total: float
    item_count: int


class AddToCartRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(1, gt=0, le=99)


# ---------- Recommendations / Bundles ----------
class RecommendationOut(BaseModel):
    product: ProductOut
    reason: str
    kind: str  # "cross_sell" | "upsell"


class BundleItemOut(BaseModel):
    product: ProductOut


class BundleOut(BaseModel):
    title: str
    items: list[BundleItemOut]
    total: float
    budget: Optional[float] = None
    within_budget: bool
    explanation: str


class BundleRequest(BaseModel):
    goal: str = Field(..., min_length=2, max_length=300)
    budget: Optional[float] = Field(None, gt=0)


class RecommendRequest(BaseModel):
    # Optional product to base cross/upsell on; otherwise uses current cart
    product_id: Optional[int] = Field(None, gt=0)


# ---------- Agent chat ----------
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)


class ChatResponse(BaseModel):
    reply: str
    intent: str
    recommendations: list[RecommendationOut] = []
    bundle: Optional[BundleOut] = None
    usage: "UsageOut"


# ---------- Usage / Subscription ----------
class UsageOut(BaseModel):
    plan: str
    limit: Optional[int]  # None means unlimited
    used: int
    remaining: Optional[int]
    period: str
    reset_period: str
    limit_reached: bool
    expires_at: Optional[datetime] = None


class SubscriptionOut(BaseModel):

    plan: str

    status: str

    started_at: datetime | None = None

    expires_at: datetime | None = None


class UpgradeRequest(BaseModel):
    plan: str = Field(..., pattern="^(free|plus)$")


class CreateOrderOut(BaseModel):
    order_id: str
    amount: int
    currency: str
    key_id: str


class VerifyPaymentRequest(BaseModel):
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str

ChatResponse.model_rebuild()

"""Authentication helpers for Cartiva."""

from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Create a secure password hash."""
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its stored hash."""
    return password_hash.verify(password, hashed_password)

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    message: str
    user_id: int
    name: str
    email: str