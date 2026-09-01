"""CartivaAgent — orchestrates the LLM provider and agent tools."""

import json
import re
from dataclasses import dataclass
from typing import Optional

from sqlalchemy.orm import Session

from app.agent.llm_provider import LLMMessage, LLMProvider
from app.agent.tools import AgentTools
from app.services import (
    bundle_service,
    cart_service,
    recommendation_service,
)
from app.services.errors import BundleNotPossible


SYSTEM_PROMPT = (
    "You are Cartiva AI, an embeddable shopping assistant. You help customers "
    "search products, optimize their cart, and build bundles within a budget. "
    "You never purchase or check out on the customer's behalf; the customer must "
    "always approve recommendations before anything is added to the cart."
)


@dataclass
class AgentResult:
    reply: str
    intent: str
    recommendations: list[dict]
    bundle: Optional[dict]


def _extract_budget(text: str) -> Optional[float]:
    match = re.search(
        r"(?:₹|rs\.?|inr)?\s*([\d,]{3,})",
        text.lower(),
    )

    if match:
        try:
            return float(match.group(1).replace(",", ""))
        except ValueError:
            return None

    return None


def _clean_search_query(text: str) -> str:
    """
    Remove common conversational phrases so product search gets
    the useful product words instead of the whole sentence.
    """

    query = text.lower().strip()

    phrases = [
        "show me",
        "show",
        "find me",
        "find",
        "get me",
        "get",
        "give me",
        "give",
        "i need to buy",
        "i need",
        "i want to buy",
        "i want",
        "i am looking for",
        "i'm looking for",
        "looking for",
        "can you show me",
        "can you find",
        "please show me",
        "please find",
        "please get me",
        "please get",
        "browse",
        "buy",
    ]

    for phrase in phrases:
        query = query.replace(phrase, " ")

    # Remove common filler words.
    filler_words = {
        "a",
        "an",
        "the",
        "some",
        "me",
        "for",
        "please",
        "to",
        "my",
        "products",
        "product",
        "items",
        "item",
    }

    words = query.split()
    words = [word for word in words if word not in filler_words]

    query = " ".join(words)

    # Normalize common punctuation.
    query = query.replace("–", " ")
    query = query.replace("—", " ")
    query = re.sub(r"\s+", " ", query).strip()

    return query


def _normalize_category(category: Optional[str]) -> Optional[str]:
    """
    Normalize category wording coming from the LLM.

    Examples:
        yoga mats -> yoga-mats
        yoga-mat -> yoga-mats
        mobile accessories -> mobile-accessories
    """

    if not category:
        return None

    category = category.lower().strip()
    category = re.sub(r"\s+", " ", category)

    replacements = {
        "yoga mat": "yoga-mats",
        "yoga mats": "yoga-mats",
        "yoga-mat": "yoga-mats",
        "mobile accessory": "mobile-accessories",
        "mobile accessories": "mobile-accessories",
        "t shirt": "tshirts",
        "t shirts": "tshirts",
        "t-shirt": "tshirts",
        "t-shirts": "tshirts",
    }

    return replacements.get(category, category)


class CartivaAgent:

    def __init__(
        self,
        db: Session,
        user_id: int,
        provider: LLMProvider,
    ):
        self.db = db
        self.user_id = user_id
        self.provider = provider
        self.tools = AgentTools(db, user_id)

    # ---------------------------------------------------------
    # UNDERSTAND CUSTOMER REQUEST
    # ---------------------------------------------------------

    def _understand_request(self, message: str) -> dict:

        response = self.provider.complete(
            messages=[
                LLMMessage(
                    role="system",
                    content=(
                        "You are the intent parser for Cartiva AI. "
                        "Understand the customer's shopping request and return "
                        "ONLY valid JSON with these fields: "
                        "shopping_intent, category, budget, goal. "

                        "shopping_intent must be one of: "
                        "get_cart, cart_total, bundle, cart_recommend, "
                        "make_cheaper, search. "

                        "Use 'get_cart' when the customer asks to see, view, "
                        "check, or inspect their cart contents. "

                        "Use 'cart_total' when the customer asks for the "
                        "total, subtotal, cost, or price of their cart. "

                        "Use 'cart_recommend' when the customer asks what "
                        "products go well with items in their cart or asks "
                        "for recommendations based on their cart. "

                        "Use 'make_cheaper' when the customer wants to reduce "
                        "the price of an existing bundle or shopping selection. "

                        "Use 'bundle' only when the customer explicitly wants "
                        "a kit, bundle, collection, routine, set, or multiple "
                        "complementary products. "

                        "Use 'search' when the customer wants to find, see, "
                        "show, browse, or get products, even when they specify "
                        "a budget. "

                        "For product searches, category should contain the "
                        "actual catalog category when you are confident. "
                        "If the customer names a specific product or brand, "
                        "put that useful product wording in category or goal. "

                        "budget must be a number or null. "

                        "category must be a short product category or null. "

                        "goal must be a short description of what the customer wants."
                    ),
                ),
                LLMMessage(
                    role="user",
                    content=message,
                ),
            ],
        )

        print(
            "DEBUG: Qwen understanding response:",
            response.content,
        )

        try:
            return json.loads(response.content)

        except json.JSONDecodeError:
            print("DEBUG: Qwen returned invalid JSON")
            return {}

    # ---------------------------------------------------------
    # FALLBACK INTENT DETECTION
    # ---------------------------------------------------------

    def _detect_intent(self, text: str) -> str:

        t = text.lower()

        if any(
            k in t
            for k in [
                "bundle",
                "kit",
                "build me",
                "routine",
                "set up",
                "starter",
                "collection",
            ]
        ):
            return "bundle"

        if any(
            k in t
            for k in [
                "cheaper",
                "reduce",
                "lower",
                "cheap",
            ]
        ):
            return "make_cheaper"

        if any(
            k in t
            for k in [
                "what should i add",
                "what goes well",
                "recommend",
                "recommendation",
                "suggest",
            ]
        ):
            return "cart_recommend"

        if any(
            k in t
            for k in [
                "what's in my cart",
                "what is in my cart",
                "show my cart",
                "view my cart",
                "check my cart",
                "see my cart",
                "my cart",
            ]
        ):
            return "get_cart"

        if any(
            k in t
            for k in [
                "cart total",
                "total of my cart",
                "total for my cart",
                "how much is my cart",
                "subtotal",
            ]
        ):
            return "cart_total"

        return "search"

    # ---------------------------------------------------------
    # PRODUCT SEARCH WITH FALLBACKS
    # ---------------------------------------------------------

    def _search_products(
        self,
        message: str,
        category: Optional[str],
        budget: Optional[float],
    ) -> dict:
        """
        Search the catalog using multiple safe strategies.

        First try the LLM category.
        If that fails, try the cleaned user query.
        If that fails, try the original user message.
        """

        normalized_category = _normalize_category(category)
        cleaned_query = _clean_search_query(message)

        print("DEBUG: Search category:", normalized_category)
        print("DEBUG: Cleaned search query:", cleaned_query)
        print("DEBUG: Search budget:", budget)

        # -----------------------------------------------------
        # Attempt 1: category search
        # -----------------------------------------------------

        if normalized_category:
            result = self.tools.search_products(
                category=normalized_category,
                max_price=budget,
                query=None,
            )

            products = result.get("products", [])

            if products:
                print(
                    "DEBUG: Category search found",
                    len(products),
                    "products",
                )
                return result

        # -----------------------------------------------------
        # Attempt 2: cleaned natural-language query
        # -----------------------------------------------------

        if cleaned_query:
            result = self.tools.search_products(
                category=None,
                max_price=budget,
                query=cleaned_query,
            )

            products = result.get("products", [])

            if products:
                print(
                    "DEBUG: Cleaned query search found",
                    len(products),
                    "products",
                )
                return result

        # -----------------------------------------------------
        # Attempt 3: original user message
        # -----------------------------------------------------

        result = self.tools.search_products(
            category=None,
            max_price=budget,
            query=message,
        )

        products = result.get("products", [])

        if products:
            print(
                "DEBUG: Original query search found",
                len(products),
                "products",
            )
            return result

        # -----------------------------------------------------
        # Nothing found
        # -----------------------------------------------------

        return {"products": []}

    # ---------------------------------------------------------
    # MAIN MESSAGE HANDLER
    # ---------------------------------------------------------

    def handle_message(self, message: str) -> AgentResult:

        print("DEBUG: About to call Qwen")

        request = self._understand_request(message)

        print("DEBUG: Parsed request:", request)

        intent = request.get(
            "shopping_intent",
            "search",
        )

        # If Qwen returns something unexpected, safely fall back.
        valid_intents = {
            "get_cart",
            "cart_total",
            "bundle",
            "cart_recommend",
            "make_cheaper",
            "search",
        }

        if intent not in valid_intents:
            print(
                "DEBUG: Invalid intent from Qwen:",
                intent,
            )
            intent = self._detect_intent(message)

        print("DEBUG: Final intent:", intent)

        # -----------------------------------------------------
        # CART CONTENTS
        # -----------------------------------------------------

        if intent == "get_cart":

            cart_result = self.tools.get_cart()

            if cart_result["item_count"] == 0:

                return AgentResult(
                    reply="Your cart is currently empty.",
                    intent="get_cart",
                    recommendations=[],
                    bundle=None,
                )

            return AgentResult(
                reply=(
                    f"Your cart has "
                    f"{cart_result['item_count']} item(s) "
                    f"with a subtotal of "
                    f"₹{cart_result['subtotal']}."
                ),
                intent="get_cart",
                recommendations=[],
                bundle=None,
            )

        # -----------------------------------------------------
        # CART TOTAL
        # -----------------------------------------------------

        if intent == "cart_total":

            total_result = self.tools.calculate_cart_total()

            return AgentResult(
                reply=(
                    f"Your cart total is "
                    f"₹{total_result['total']}."
                ),
                intent="cart_total",
                recommendations=[],
                bundle=None,
            )

        # -----------------------------------------------------
        # BUNDLE / MAKE CHEAPER
        # -----------------------------------------------------

        if intent in (
            "bundle",
            "make_cheaper",
        ):

            budget = (
                request.get("budget")
                or _extract_budget(message)
            )

            try:

                bundle = bundle_service.build_bundle(
                    self.db,
                    goal=message,
                    budget=budget,
                )

            except BundleNotPossible as e:

                return AgentResult(
                    reply=e.message,
                    intent="bundle",
                    recommendations=[],
                    bundle=None,
                )

            reply = (
                f"I can build one for you. Here's a bundle "
                f"that fits your budget — "
                f"{bundle['title']} for "
                f"₹{int(bundle['total'])}. "
                "You can add it, make it cheaper, "
                "or change the products."
            )

            return AgentResult(
                reply=reply,
                intent="bundle",
                recommendations=[],
                bundle=bundle,
            )

        # -----------------------------------------------------
        # CART RECOMMENDATIONS
        # -----------------------------------------------------

        if intent == "cart_recommend":

            cart = cart_service.get_or_create_cart(
                self.db,
                self.user_id,
            )

            recs = recommendation_service.recommend_for_cart(
                self.db,
                cart,
            )

            if not recs:

                return AgentResult(
                    reply=(
                        "Your cart is empty or I don't have "
                        "suggestions yet. Try adding a product "
                        "first, then ask me what goes well with it."
                    ),
                    intent="cart_recommend",
                    recommendations=[],
                    bundle=None,
                )

            return AgentResult(
                reply=(
                    "Based on your cart, here are a few products "
                    "that work well together. Add any you like — "
                    "nothing is added without your approval."
                ),
                intent="cart_recommend",
                recommendations=recs,
                bundle=None,
            )

        # -----------------------------------------------------
        # PRODUCT SEARCH
        # -----------------------------------------------------

        category = request.get("category")
        budget = request.get("budget")

        if budget is None:
            budget = _extract_budget(message)

        result = self._search_products(
            message=message,
            category=category,
            budget=budget,
        )

        products = result.get("products", [])

        if not products:

            return AgentResult(
                reply=(
                    "I couldn't find matching products. "
                    "Try a different keyword, category, "
                    "or ask me to build a bundle for a goal."
                ),
                intent="search",
                recommendations=[],
                bundle=None,
            )

        from app.services.product_service import get_product

        recs = [
            {
                "product": get_product(
                    self.db,
                    p["id"],
                ),
                "reason": (
                    f"Matches your search in "
                    f"{p['category']}."
                ),
                "kind": "cross_sell",
            }
            for p in products[:4]
        ]

        return AgentResult(
            reply=(
                f"I found {len(products)} products. "
                "Here are a few good matches."
            ),
            intent="search",
            recommendations=recs,
            bundle=None,
        )