"""
Pydantic response schemas for the Bank Interest Rates domain.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BankRateOut(BaseModel):
    """Single bank interest rate record."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    bank_code: str
    bank_name: str
    term_months: int
    interest_rate: Decimal
    rate_type: str
    currency: str
    min_deposit: Optional[Decimal] = None
    source: str
    scraped_at: datetime
    created_at: datetime


class BankRateLatestOut(BaseModel):
    """Wrapper for a list of bank rate records."""

    count: int
    data: list[BankRateOut]


class BankListOut(BaseModel):
    """List of distinct banks."""

    banks: list[dict]


class ScrapeResultOut(BaseModel):
    """Result of a manual scrape trigger."""

    status: str
    records_saved: int
    message: str
