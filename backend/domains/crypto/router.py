"""
API routes for the Cryptocurrency domain.
"""

from typing import Optional

from fastapi import APIRouter, Query
from sqlalchemy import desc, func

from core.db import SessionDep
from core.params import HistoryParamsDep
from domains.crypto.models import CryptoPrice
from domains.crypto.schemas import (
    CryptoPriceLatestOut,
    ScrapeResultOut,
    SymbolListOut,
)
from domains.crypto.scraper import scrape_crypto

router = APIRouter(
    prefix="/crypto",
    tags=["Cryptocurrency"],
)


@router.get("/latest", response_model=CryptoPriceLatestOut)
def get_latest_crypto_prices(
    db: SessionDep,
    symbol: Optional[str] = Query(None, description="Filter by symbol (e.g. BTC, ETH)"),
):
    """Get the latest price for each cryptocurrency symbol."""
    sub = db.query(
        CryptoPrice.symbol,
        func.max(CryptoPrice.scraped_at).label("max_scraped"),
    ).group_by(CryptoPrice.symbol)
    if symbol:
        sub = sub.filter(CryptoPrice.symbol == symbol.upper())
    sub = sub.subquery()

    query = (
        db.query(CryptoPrice)
        .join(
            sub,
            (CryptoPrice.symbol == sub.c.symbol)
            & (CryptoPrice.scraped_at == sub.c.max_scraped),
        )
        .order_by(desc(CryptoPrice.market_cap_usd))
    )

    results = query.all()
    return CryptoPriceLatestOut(count=len(results), data=results)


@router.get("/history", response_model=CryptoPriceLatestOut)
def get_crypto_history(
    db: SessionDep,
    params: HistoryParamsDep,
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
):
    """Get historical crypto prices with optional filters and pagination."""
    query = db.query(CryptoPrice)

    if symbol:
        query = query.filter(CryptoPrice.symbol == symbol.upper())
    if params.start_date:
        query = query.filter(CryptoPrice.scraped_at >= params.start_date)
    if params.end_date:
        query = query.filter(CryptoPrice.scraped_at <= params.end_date)

    query = (
        query.order_by(desc(CryptoPrice.scraped_at))
        .offset(params.offset)
        .limit(params.limit)
    )
    results = query.all()
    return CryptoPriceLatestOut(count=len(results), data=results)


@router.get("/symbols", response_model=SymbolListOut)
def get_symbols(db: SessionDep):
    """List all distinct cryptocurrency symbols."""
    symbols = (
        db.query(
            CryptoPrice.symbol,
            CryptoPrice.name,
        )
        .distinct()
        .order_by(CryptoPrice.symbol)
        .all()
    )
    return SymbolListOut(symbols=[{"symbol": s[0], "name": s[1]} for s in symbols])


@router.post("/scrape", response_model=ScrapeResultOut)
def trigger_crypto_scrape():
    """Manually trigger the cryptocurrency scraper."""
    try:
        count = scrape_crypto()
        return ScrapeResultOut(
            status="success",
            records_saved=count,
            message=f"Scraped and saved {count} crypto price records",
        )
    except Exception as exc:
        return ScrapeResultOut(
            status="error",
            records_saved=0,
            message=f"Scrape failed: {exc}",
        )
