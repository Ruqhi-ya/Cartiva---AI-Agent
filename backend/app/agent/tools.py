"""Agent tools — the function-calling surface for Cartiva AI.

Each tool has a clear name, description, validated input and structured output.
Tools are backed by the services layer and PostgreSQL. They are the ONLY way
the agent touches data, which keeps the LLM sandboxed to safe operations.

Note: add_to_cart is executed only after explicit customer approval in the UI;
the agent never purchases or checks out on its own.
"""
from typing import Any, Callable, Optional

from sqlalchemy.orm import Session

from app.agent.llm_provider import ToolSpec
from app.services import (
    bundle_service,
    cart_service,
    product_service,
    recommendation_service,
    usage_service,
)
from app.services.errors import CartivaError


def _product_dict(p) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "category": p.category,
        "price": p.price,
        "stock": p.stock,
        "is_premium": p.is_premium,
    }


class AgentTools:
    """Concrete tool implementations bound to a DB session and user."""

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    # ---- Tool implementations (structured dict output) ----
    def search_products(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        max_price: Optional[float] = None,
    ) -> dict:
        products = product_service.search_products(
            self.db, query=query, category=category, max_price=max_price
        )
        return {"products": [_product_dict(p) for p in products]}

    def get_product_details(self, product_id: int) -> dict:
        p = product_service.get_product(self.db, product_id)
        return {
            "product": {
                **_product_dict(p),
                "description": p.description,
                "tags": p.tags,
            }
        }

    def get_cart(self) -> dict:
        cart = cart_service.get_or_create_cart(self.db, self.user_id)
        data = cart_service.serialize_cart(self.db, cart)
        return {
            "item_count": data["item_count"],
            "subtotal": data["subtotal"],
            "items": [
                {"id": i["id"], "name": i["product"].name, "quantity": i["quantity"]}
                for i in data["items"]
            ],
        }

    def calculate_cart_total(self) -> dict:
        cart = cart_service.get_or_create_cart(self.db, self.user_id)
        return cart_service.calculate_total(self.db, cart)

    def find_related_products(self, product_id: int) -> dict:
        related = product_service.find_related(self.db, product_id)
        return {"products": [_product_dict(p) for p in related]}

    def create_bundle(self, goal: str, budget: Optional[float] = None) -> dict:
        bundle = bundle_service.build_bundle(self.db, goal=goal, budget=budget)
        return {
            "title": bundle["title"],
            "total": bundle["total"],
            "within_budget": bundle["within_budget"],
            "items": [_product_dict(i["product"]) for i in bundle["items"]],
        }

    def add_to_cart(self, product_id: int, quantity: int = 1) -> dict:
        """Requires prior customer approval (enforced at the API layer)."""
        cart = cart_service.add_item(self.db, self.user_id, product_id, quantity)
        return cart_service.calculate_total(self.db, cart)

    def remove_from_cart(self, item_id: int) -> dict:
        cart = cart_service.remove_item(self.db, self.user_id, item_id)
        return cart_service.calculate_total(self.db, cart)

    def check_usage_limit(self) -> dict:
        return usage_service.check_usage_limit(self.db, self.user_id)

    # ---- Dispatch ----
    def registry(self) -> dict[str, Callable[..., dict]]:
        return {
            "search_products": self.search_products,
            "get_product_details": self.get_product_details,
            "get_cart": self.get_cart,
            "calculate_cart_total": self.calculate_cart_total,
            "find_related_products": self.find_related_products,
            "create_bundle": self.create_bundle,
            "add_to_cart": self.add_to_cart,
            "remove_from_cart": self.remove_from_cart,
            "check_usage_limit": self.check_usage_limit,
        }

    def call(self, name: str, arguments: dict[str, Any]) -> dict:
        """Invoke a tool by name with structured error handling."""
        fn = self.registry().get(name)
        if not fn:
            return {"error": f"Unknown tool: {name}"}
        try:
            return fn(**arguments)
        except CartivaError as e:
            return {"error": e.message}
        except TypeError as e:
            return {"error": f"Invalid arguments for {name}: {e}"}


# Tool specifications advertised to the LLM. This is what enables function
# calling once a real provider is connected.
TOOL_SPECS: list[ToolSpec] = [
    ToolSpec(
        name="search_products",
        description="Search the product catalog by keyword, category or max price.",
        parameters={
            "query": "string|null",
            "category": "string|null",
            "max_price": "number|null",
        },
    ),
    ToolSpec(
        name="get_product_details",
        description="Get full details for a single product by id.",
        parameters={"product_id": "integer"},
    ),
    ToolSpec(
        name="get_cart",
        description="Inspect the customer's current cart contents.",
        parameters={},
    ),
    ToolSpec(
        name="calculate_cart_total",
        description="Calculate the subtotal/total of the current cart (server-side).",
        parameters={},
    ),
    ToolSpec(
        name="find_related_products",
        description="Find products related to a given product (cross/upsell).",
        parameters={"product_id": "integer"},
    ),
    ToolSpec(
        name="create_bundle",
        description="Build a dynamic product bundle for a goal within an optional budget.",
        parameters={"goal": "string", "budget": "number|null"},
    ),
    ToolSpec(
        name="add_to_cart",
        description="Add a product to the cart. Only after explicit customer approval.",
        parameters={"product_id": "integer", "quantity": "integer"},
    ),
    ToolSpec(
        name="remove_from_cart",
        description="Remove an item from the cart by cart item id.",
        parameters={"item_id": "integer"},
    ),
    ToolSpec(
        name="check_usage_limit",
        description="Check the customer's remaining AI usage for the period.",
        parameters={},
    ),
]
