"""
Pydantic response schemas for the Cryptocurrency domain.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CryptoPriceOut(BaseModel):
    """Single cryptocurrency price record."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str
    name: str
    price_usd: Decimal
    price_vnd: Optional[Decimal] = None
    market_cap_usd: Optional[Decimal] = None
    volume_24h_usd: Optional[Decimal] = None
    change_24h_pct: Optional[Decimal] = None
    source: str
    scraped_at: datetime
    created_at: datetime


class CryptoPriceLatestOut(BaseModel):
    """Wrapper for a list of crypto price records."""

    count: int
    data: list[CryptoPriceOut]


class SymbolListOut(BaseModel):
    """List of distinct crypto symbols."""

    symbols: list[dict]


class ScrapeResultOut(BaseModel):
    """Result of a manual scrape trigger."""

    status: str
    records_saved: int
    message: str
