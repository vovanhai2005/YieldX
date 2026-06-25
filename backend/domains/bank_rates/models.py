"""
ORM model for Vietnamese bank deposit interest rate time-series data.

Covers banks such as Vietcombank, BIDV, Agribank, Techcombank, VPBank, MB, etc.
Each row captures a single (bank, term, rate_type, currency) snapshot.

Key indexes
───────────
• (bank_code, term_months, scraped_at DESC)  →  "latest 12-month rate at VCB"
• (bank_code, scraped_at DESC)               →  "all current rates for a bank"
• (scraped_at)                               →  cross-bank time-range scans
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Index, Numeric, SmallInteger, String, desc
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base, TimeSeriesMixin


class BankInterestRate(Base, TimeSeriesMixin):
    """Snapshot of a bank's deposit interest rate for a specific term."""

    __tablename__ = "bank_interest_rates"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    bank_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Bank code: VCB, BIDV, AGR, TCB, VPB, MBB, …",
    )
    bank_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Full name: Vietcombank, BIDV, Agribank, Techcombank, …",
    )
    term_months: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        comment="Deposit term in months: 1, 3, 6, 9, 12, 13, 18, 24, 36",
    )
    interest_rate: Mapped[Decimal] = mapped_column(
        Numeric(6, 3),
        nullable=False,
        comment="Annual interest rate as percentage, e.g. 5.500 = 5.5%%/year",
    )
    rate_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default="counter",
        comment="Rate channel: counter, online",
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        server_default="VND",
        comment="Deposit currency: VND, USD",
    )
    min_deposit: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 0),
        nullable=True,
        comment="Minimum deposit amount (VND) if applicable",
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
            "ix_bank_rates_code_term_scraped",
            "bank_code",
            "term_months",
            desc("scraped_at"),
        ),
        Index(
            "ix_bank_rates_code_scraped",
            "bank_code",
            desc("scraped_at"),
        ),
        Index("ix_bank_rates_scraped_at", "scraped_at"),
        {"comment": "Bank deposit interest rates from Vietnamese banks"},
    )

    def __repr__(self) -> str:
        return (
            f"<BankInterestRate(bank='{self.bank_code}', term={self.term_months}m, "
            f"rate={self.interest_rate}%, type='{self.rate_type}', at={self.scraped_at})>"
        )
