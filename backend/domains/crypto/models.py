"""
ORM model for cryptocurrency price time-series data.

Sources include CoinGecko, CoinMarketCap, Binance, etc.
Each row captures a single (symbol, source) price snapshot with market metrics.

Key indexes
───────────
• (symbol, scraped_at DESC)  →  "latest BTC price"
• (scraped_at)               →  cross-symbol time-range scans
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Index, Numeric, String, desc
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base, TimeSeriesMixin


class CryptoPrice(Base, TimeSeriesMixin):
    """Snapshot of a cryptocurrency's price and market metrics."""

    __tablename__ = "crypto_prices"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Ticker symbol: BTC, ETH, BNB, SOL, XRP, …",
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Full name: Bitcoin, Ethereum, Solana, …",
    )
    price_usd: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        nullable=False,
        comment="Price in USD",
    )
    price_vnd: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(20, 0),
        nullable=True,
        comment="Price in VND (converted)",
    )
    market_cap_usd: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(24, 0),
        nullable=True,
        comment="Market capitalization in USD",
    )
    volume_24h_usd: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(24, 0),
        nullable=True,
        comment="24-hour trading volume in USD",
    )
    change_24h_pct: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 4),
        nullable=True,
        comment="24-hour price change percentage",
    )
    source: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Data source: CoinGecko, CoinMarketCap, Binance, …",
    )
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Timestamp when data was scraped from the source",
    )

    __table_args__ = (
        Index(
            "ix_crypto_symbol_scraped",
            "symbol",
            desc("scraped_at"),
        ),
        Index("ix_crypto_scraped_at", "scraped_at"),
        {"comment": "Cryptocurrency prices and market data"},
    )

    def __repr__(self) -> str:
        return (
            f"<CryptoPrice(symbol='{self.symbol}', price_usd={self.price_usd}, "
            f"change_24h={self.change_24h_pct}%, at={self.scraped_at})>"
        )
