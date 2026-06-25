"""
API routes for the Forex Rates domain.
"""

from typing import Optional

from fastapi import APIRouter, Query
from sqlalchemy import desc, func

from core.db import SessionDep
from core.params import HistoryParamsDep
from domains.forex.models import ForexRate
from domains.forex.schemas import (
    CurrencyListOut,
    ForexRateLatestOut,
    ScrapeResultOut,
)
from domains.forex.scraper import scrape_forex

router = APIRouter(
    prefix="/forex",
    tags=["Forex Rates"],
)


@router.get("/latest", response_model=ForexRateLatestOut)
def get_latest_forex_rates(
    db: SessionDep,
    currency_code: Optional[str] = Query(
        None, description="Filter by currency code (e.g. USD, EUR)"
    ),
    source: Optional[str] = Query(
        None, description="Filter by source (e.g. Vietcombank)"
    ),
):
    """Get the latest exchange rate for each (currency_code, source) pair."""
    sub = db.query(
        ForexRate.currency_code,
        ForexRate.source,
        func.max(ForexRate.scraped_at).label("max_scraped"),
    ).group_by(ForexRate.currency_code, ForexRate.source)
    if currency_code:
        sub = sub.filter(ForexRate.currency_code == currency_code.upper())
    if source:
        sub = sub.filter(ForexRate.source == source)
    sub = sub.subquery()

    query = (
        db.query(ForexRate)
        .join(
            sub,
            (ForexRate.currency_code == sub.c.currency_code)
            & (ForexRate.source == sub.c.source)
            & (ForexRate.scraped_at == sub.c.max_scraped),
        )
        .order_by(ForexRate.currency_code)
    )

    results = query.all()
    return ForexRateLatestOut(count=len(results), data=results)


@router.get("/history", response_model=ForexRateLatestOut)
def get_forex_history(
    db: SessionDep,
    params: HistoryParamsDep,
    currency_code: Optional[str] = Query(None, description="Filter by currency code"),
    source: Optional[str] = Query(None, description="Filter by source"),
):
    """Get historical forex rates with optional filters and pagination."""
    query = db.query(ForexRate)

    if currency_code:
        query = query.filter(ForexRate.currency_code == currency_code.upper())
    if source:
        query = query.filter(ForexRate.source == source)
    if params.start_date:
        query = query.filter(ForexRate.scraped_at >= params.start_date)
    if params.end_date:
        query = query.filter(ForexRate.scraped_at <= params.end_date)

    query = (
        query.order_by(desc(ForexRate.scraped_at))
        .offset(params.offset)
        .limit(params.limit)
    )
    results = query.all()
    return ForexRateLatestOut(count=len(results), data=results)


@router.get("/currencies", response_model=CurrencyListOut)
def get_currencies(db: SessionDep):
    """List all distinct currencies."""
    currencies = (
        db.query(
            ForexRate.currency_code,
            ForexRate.currency_name,
        )
        .distinct()
        .order_by(ForexRate.currency_code)
        .all()
    )
    return CurrencyListOut(
        currencies=[{"code": c[0], "name": c[1]} for c in currencies]
    )


@router.post("/scrape", response_model=ScrapeResultOut)
def trigger_forex_scrape():
    """Manually trigger the forex exchange rate scraper."""
    try:
        count = scrape_forex()
        return ScrapeResultOut(
            status="success",
            records_saved=count,
            message=f"Scraped and saved {count} forex rate records",
        )
    except Exception as exc:
        return ScrapeResultOut(
            status="error",
            records_saved=0,
            message=f"Scrape failed: {exc}",
        )
