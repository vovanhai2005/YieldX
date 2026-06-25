"""
API routes for the Gold Price domain.
"""

from typing import Optional

from fastapi import APIRouter, Query
from sqlalchemy import desc, distinct, func

from core.db import SessionDep
from core.params import HistoryParamsDep
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
    db: SessionDep,
    brand: Optional[str] = Query(None, description="Filter by brand (e.g. SJC, DOJI)"),
):
    """Get the latest gold price for each (brand, product_type) pair."""
    # Subquery: max scraped_at per (brand, product_type)
    sub = db.query(
        GoldPrice.brand,
        GoldPrice.product_type,
        func.max(GoldPrice.scraped_at).label("max_scraped"),
    ).group_by(GoldPrice.brand, GoldPrice.product_type)
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
    db: SessionDep,
    params: HistoryParamsDep,
    brand: Optional[str] = Query(None, description="Filter by brand"),
    product_type: Optional[str] = Query(None, description="Filter by product type"),
):
    """Get historical gold prices with optional filters and pagination."""
    query = db.query(GoldPrice)

    if brand:
        query = query.filter(GoldPrice.brand == brand)
    if product_type:
        query = query.filter(GoldPrice.product_type == product_type)
    if params.start_date:
        query = query.filter(GoldPrice.scraped_at >= params.start_date)
    if params.end_date:
        query = query.filter(GoldPrice.scraped_at <= params.end_date)

    query = (
        query.order_by(desc(GoldPrice.scraped_at))
        .offset(params.offset)
        .limit(params.limit)
    )
    results = query.all()
    return GoldPriceLatestOut(count=len(results), data=results)


@router.get("/brands", response_model=GoldBrandsOut)
def get_gold_brands(db: SessionDep):
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
