"""
API routes for the Gold Price domain.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, distinct, func
from sqlalchemy.orm import Session

from core.db import get_db
from domains.gold.models import GoldPrice
from domains.gold.schemas import (
    GoldBrandsOut,
    GoldPriceLatestOut,
    GoldPriceOut,
    ScrapeResultOut,
)
from domains.gold.scraper import scrape_gold

router = APIRouter(
    prefix="/gold",
    tags=["Gold Price"],
)


@router.get("/latest", response_model=GoldPriceLatestOut)
def get_latest_gold_prices(
    brand: Optional[str] = Query(None, description="Filter by brand (e.g. SJC, DOJI)"),
    db: Session = Depends(get_db),
):
    """Get the latest gold price for each (brand, product_type) pair."""
    # Subquery: max scraped_at per (brand, product_type)
    sub = (
        db.query(
            GoldPrice.brand,
            GoldPrice.product_type,
            func.max(GoldPrice.scraped_at).label("max_scraped"),
        )
        .group_by(GoldPrice.brand, GoldPrice.product_type)
    )
    if brand:
        sub = sub.filter(GoldPrice.brand == brand)
    sub = sub.subquery()

    query = (
        db.query(GoldPrice)
        .join(
            sub,
            (GoldPrice.brand == sub.c.brand)
            & (GoldPrice.product_type == sub.c.product_type)
            & (GoldPrice.scraped_at == sub.c.max_scraped),
        )
        .order_by(GoldPrice.brand, GoldPrice.product_type)
    )

    results = query.all()
    return GoldPriceLatestOut(count=len(results), data=results)


@router.get("/history", response_model=GoldPriceLatestOut)
def get_gold_history(
    brand: Optional[str] = Query(None, description="Filter by brand"),
    product_type: Optional[str] = Query(None, description="Filter by product type"),
    start_date: Optional[datetime] = Query(None, description="Start date (ISO 8601)"),
    end_date: Optional[datetime] = Query(None, description="End date (ISO 8601)"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Records to skip"),
    db: Session = Depends(get_db),
):
    """Get historical gold prices with optional filters and pagination."""
    query = db.query(GoldPrice)

    if brand:
        query = query.filter(GoldPrice.brand == brand)
    if product_type:
        query = query.filter(GoldPrice.product_type == product_type)
    if start_date:
        query = query.filter(GoldPrice.scraped_at >= start_date)
    if end_date:
        query = query.filter(GoldPrice.scraped_at <= end_date)

    query = query.order_by(desc(GoldPrice.scraped_at)).offset(offset).limit(limit)
    results = query.all()
    return GoldPriceLatestOut(count=len(results), data=results)


@router.get("/brands", response_model=GoldBrandsOut)
def get_gold_brands(db: Session = Depends(get_db)):
    """List all distinct gold brands."""
    brands = db.query(distinct(GoldPrice.brand)).order_by(GoldPrice.brand).all()
    return GoldBrandsOut(brands=[b[0] for b in brands])


@router.post("/scrape", response_model=ScrapeResultOut)
def trigger_gold_scrape():
    """Manually trigger the gold price scraper."""
    try:
        count = scrape_gold()
        return ScrapeResultOut(
            status="success",
            records_saved=count,
            message=f"Scraped and saved {count} gold price records",
        )
    except Exception as exc:
        return ScrapeResultOut(
            status="error",
            records_saved=0,
            message=f"Scrape failed: {exc}",
        )