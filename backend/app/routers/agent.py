"""Cartiva AI agent endpoints.

/chat consumes one AI session (usage tracked + limited for free users).
/recommend and /bundle are supporting actions used by the UI (Make It Cheaper,
Smart Cart Optimizer). None of these ever add to the cart automatically — the
customer approves additions via the standard cart endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agent.cartiva_agent import CartivaAgent
from app.agent.llm_provider import get_provider
from app.config import settings
from app.database import get_db
from app.deps import get_current_user_id
from app.schemas import (
    BundleOut,
    BundleRequest,
    ChatRequest,
    ChatResponse,
    RecommendationOut,
    RecommendRequest,
)
from app.services import (
    bundle_service,
    cart_service,
    recommendation_service,
    usage_service,
)

router = APIRouter(prefix="/api/agent", tags=["agent"])


def _provider():
    return get_provider(settings.LLM_PROVIDER, settings.LLM_API_KEY, settings.LLM_MODEL)


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    
    try:
        user_id = get_current_user_id(db)

        usage_service.consume_session(db, user_id)

        agent = CartivaAgent(db, user_id, _provider())

        result = agent.handle_message(payload.message)

        usage = usage_service.get_usage(db, user_id)

        return ChatResponse(
            reply=result.reply,
            intent=result.intent,
            recommendations=[
                RecommendationOut(**r)
                for r in result.recommendations
            ],
            bundle=BundleOut(**result.bundle) if result.bundle else None,
            usage=usage,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"{type(e).__name__}: {str(e)}"
        )

@router.post("/recommend", response_model=list[RecommendationOut])
def recommend(payload: RecommendRequest, db: Session = Depends(get_db)):
    """Smart Cart Optimizer suggestions (read-only, no usage consumed)."""
    user_id = get_current_user_id(db)
    if payload.product_id:
        recs = recommendation_service.recommend_for_product(db, payload.product_id)
    else:
        cart = cart_service.get_or_create_cart(db, user_id)
        recs = recommendation_service.recommend_for_cart(db, cart)
    return [RecommendationOut(**r) for r in recs]


@router.post("/bundle", response_model=BundleOut)
def bundle(payload: BundleRequest, db: Session = Depends(get_db)):
    """Rebuild/modify a bundle (e.g. Make It Cheaper). No usage consumed."""
    b = bundle_service.build_bundle(db, goal=payload.goal, budget=payload.budget)
    return BundleOut(**b)
