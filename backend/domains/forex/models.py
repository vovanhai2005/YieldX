"""
ORM model for Vietnamese forex exchange rate time-series data.

Sources include bank rates (Vietcombank, BIDV, …) and the State Bank of Vietnam (SBV).
Each row captures a single (currency, source) exchange-rate snapshot.

Key indexes
───────────
• (currency_code, source, scraped_at DESC)  →  "latest USD rate from VCB"
• (source, scraped_at DESC)                 →  "all rates from a source"
• (scraped_at)                              →  cross-currency time-range scans
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Index, Numeric, String, desc
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base, TimeSeriesMixin


class ForexRate(Base, TimeSeriesMixin):
    """Snapshot of a foreign currency's exchange rate against VND."""

    __tablename__ = "forex_rates"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    currency_code: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        comment="ISO 4217 code: USD, EUR, GBP, JPY, CNY, …",
    )
    currency_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Currency name: US Dollar, Euro, British Pound, …",
    )
    buy_cash: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 4),
        nullable=True,
        comment="Cash buying rate in VND",
    )
    buy_transfer: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 4),
        nullable=True,
        comment="Transfer buying rate in VND",
    )
    sell: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 4),
        nullable=True,
        comment="Selling rate in VND",
    )
    source: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Data source: Vietcombank, BIDV, SBV, …",
    )
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Timestamp when data was scraped from the source",
    )

    __table_args__ = (
        Index(
            "ix_forex_code_source_scraped",
            "currency_code",
            "source",
            desc("scraped_at"),
        ),
        Index(
            "ix_forex_source_scraped",
            "source",
            desc("scraped_at"),
        ),
        Index("ix_forex_scraped_at", "scraped_at"),
        {"comment": "Foreign exchange rates from Vietnamese banks and SBV"},
    )

    def __repr__(self) -> str:
        return (
            f"<ForexRate(currency='{self.currency_code}', source='{self.source}', "
            f"buy_cash={self.buy_cash}, sell={self.sell}, at={self.scraped_at})>"
        )
