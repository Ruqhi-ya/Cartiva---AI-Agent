"""Cartiva FastAPI application entrypoint.

Registers routers, CORS, and a global handler that maps domain errors to
user-friendly JSON — raw backend errors are never surfaced to customers.
"""
import logging

logging.basicConfig(level=logging.DEBUG)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import Base, engine
from app.routers import agent, auth, cart, products, subscription, usage
from app.services.errors import CartivaError

logger = logging.getLogger("cartiva")

app = FastAPI(title="Cartiva API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup():
    # Create tables if they don't exist (simple MVP bootstrap).
    Base.metadata.create_all(bind=engine)


@app.exception_handler(CartivaError)
async def cartiva_error_handler(_: Request, exc: CartivaError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.exception_handler(Exception)
async def unhandled_error_handler(_: Request, exc: Exception):
    logger.exception("Unhandled Cartiva error")

    return JSONResponse(
        status_code=500,
        content={
            "detail": "something went wrong. please try agsin."
        },
    )


@app.get("/api/health")
def health():
    return {"status": "ok"}


app.include_router(products.router)
app.include_router(cart.router)
app.include_router(agent.router)
app.include_router(usage.router)
app.include_router(subscription.router)
app.include_router(auth.router)