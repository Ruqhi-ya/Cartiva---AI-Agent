"""Product catalog endpoints."""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ProductOut
from app.services import product_service

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=list[ProductOut])
def list_products(
    q: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    max_price: Optional[float] = Query(None),
    db: Session = Depends(get_db),
):
    return product_service.search_products(
        db, query=q, category=category, max_price=max_price
    )


@router.get("/categories", response_model=list[str])
def categories(db: Session = Depends(get_db)):
    return product_service.list_categories(db)


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return product_service.get_product(db, product_id)
