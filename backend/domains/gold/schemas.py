"""
Pydantic response schemas for the Gold Price domain.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class GoldPriceOut(BaseModel):
    """Single gold price record."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    brand: str
    product_type: str
    buy_price: Optional[Decimal] = None
    sell_price: Optional[Decimal] = None
    source: str
    scraped_at: datetime
    created_at: datetime


class GoldPriceLatestOut(BaseModel):
    """Wrapper for a list of latest gold prices."""

    count: int
    data: list[GoldPriceOut]


class GoldBrandsOut(BaseModel):
    """List of distinct gold brands."""

    brands: list[str]


class ScrapeResultOut(BaseModel):
    """Result of a manual scrape trigger."""

    status: str
    records_saved: int
    message: str
