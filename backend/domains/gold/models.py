"""
ORM model for Vietnamese gold price time-series data.

Covers dealers such as SJC, PNJ, DOJI, Bảo Tín Minh Châu, etc.
Each row captures a single (brand, product_type) price snapshot.

Key indexes
───────────
• (brand, product_type, scraped_at DESC)  →  "latest price for SJC Vàng miếng"
• (scraped_at)                            →  cross-brand time-range scans
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Index, Numeric, String, desc
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base, TimeSeriesMixin


class GoldPrice(Base, TimeSeriesMixin):
    """Snapshot of a gold product's buy/sell price from a Vietnamese dealer."""

    __tablename__ = "gold_prices"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    brand: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Dealer brand: SJC, PNJ, DOJI, Bảo Tín Minh Châu, …",
    )
    product_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Product: Vàng miếng SJC, Vàng nhẫn SJC 99.99, …",
    )
    buy_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 0),
        nullable=True,
        comment="Buy price in VND per lượng",
    )
    sell_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 0),
        nullable=True,
        comment="Sell price in VND per lượng",
    )
    source: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Data source URL or identifier",
    )
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Timestamp when data was scraped from the source",
    )

    __table_args__ = (
        Index(
            "ix_gold_brand_type_scraped",
            "brand",
            "product_type",
            desc("scraped_at"),
        ),
        Index("ix_gold_scraped_at", "scraped_at"),
        {"comment": "Gold buy/sell prices from Vietnamese dealers"},
    )

    def __repr__(self) -> str:
        return (
            f"<GoldPrice(brand='{self.brand}', type='{self.product_type}', "
            f"buy={self.buy_price}, sell={self.sell_price}, at={self.scraped_at})>"
        )
