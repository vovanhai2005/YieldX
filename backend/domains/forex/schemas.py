"""
Pydantic response schemas for the Forex Rates domain.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ForexRateOut(BaseModel):
    """Single forex exchange rate record."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    currency_code: str
    currency_name: str
    buy_cash: Optional[Decimal] = None
    buy_transfer: Optional[Decimal] = None
    sell: Optional[Decimal] = None
    source: str
    scraped_at: datetime
    created_at: datetime


class ForexRateLatestOut(BaseModel):
    """Wrapper for a list of forex rate records."""

    count: int
    data: list[ForexRateOut]


class CurrencyListOut(BaseModel):
    """List of distinct currencies."""

    currencies: list[dict]


class ScrapeResultOut(BaseModel):
    """Result of a manual scrape trigger."""

    status: str
    records_saved: int
    message: str
