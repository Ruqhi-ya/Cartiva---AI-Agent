# Cartiva

**AI-powered shopping that builds a better cart.**

Cartiva is an embeddable AI shopping assistant for online stores. It understands
a customer's shopping intent, optimizes their cart, and dynamically builds product
bundles — always requiring explicit customer approval before adding anything to
the cart. Cartiva never purchases or checks out on the customer's behalf.

This is the MVP foundation. An external LLM and Razorpay payments are **not**
integrated yet; both have clean integration points ready for a later task.

## Architecture

```
Frontend (Next.js + React + TS + Tailwind)
   └── REST → Backend (FastAPI)
                 ├── Routers  (products, cart, agent, usage/subscription)
                 ├── CartivaAgent → LLMProvider (abstract; mock for now)
                 │        └── AgentTools (9 function-calling tools)
                 ├── Services (product, cart, recommendation, bundle,
                 │             usage, subscription)
                 └── PostgreSQL (SQLAlchemy models)
```

### Agent tools (function-calling surface)
`search_products`, `get_product_details`, `get_cart`, `calculate_cart_total`,
`find_related_products`, `create_bundle`, `add_to_cart`, `remove_from_cart`,
`check_usage_limit` — all in `backend/app/agent/tools.py`, backed by services.

### LLM integration point
`backend/app/agent/llm_provider.py` defines `LLMProvider` plus a `MockLLMProvider`.
Add a real provider there and select it with `LLM_PROVIDER` — no app restructuring.

### Payment integration point
`backend/app/services/subscription_service.py` + the `Subscription.provider*`
fields are where Razorpay Test Mode connects later.

## Screens
1. **Store** (`/`) — browse/search products, add to cart, entry point to AI.
2. **Cartiva AI** (`/cartiva-ai`) — main screen: chat, recommendations, bundles.
3. **Cart / Checkout** (`/cart`) — items, smart recommendations, order summary.
4. **Cartiva Plus** (`/plus`) — plan comparison + upgrade.

## Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ (running and reachable)

## Backend setup

```bash
cd backend
python -m pip install -r requirements.txt
copy .env.example .env         # (Windows)  or: cp .env.example .env
# Edit .env: set DATABASE_URL to your Postgres instance.
# Leave LLM_* and RAZORPAY_* empty — integrated later.

python -m app.seed             # create tables + demo data
python -m uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

Key env vars (see `backend/.env.example`):
- `DATABASE_URL` — Postgres connection (uses the psycopg v3 driver).
- `FREE_MONTHLY_AI_SESSIONS` — configurable free-tier limit (default `10`).
- `LLM_*`, `RAZORPAY_*` — intentionally empty in the MVP.

## Frontend setup

```bash
cd frontend
npm install
copy .env.local.example .env.local   # (Windows)  or: cp ...
npm run dev
```

App: http://localhost:3000

## Notes on scope
- Single seeded demo customer (`demo@cartiva.app`) stands in for auth.
- Cart totals are always computed on the backend; frontend prices are ignored.
- Free users get a monthly AI-session limit; reaching it shows an upgrade flow.
- Cartiva Plus is treated as unlimited. Switching plans simulates the state
  change that Razorpay will drive later — no real billing occurs.
```
