"""
API routes for the Bank Interest Rates domain.
"""

from typing import Optional

from fastapi import APIRouter, Query
from sqlalchemy import desc, distinct, func

from core.db import SessionDep
from core.params import HistoryParamsDep
from domains.bank_rates.deps import ExistingBankDep
from domains.bank_rates.models import BankInterestRate
from domains.bank_rates.schemas import (
    BankListOut,
    BankRateLatestOut,
    BankRateOut,
    ScrapeResultOut,
)
from domains.bank_rates.scraper import scrape_bank_rates

router = APIRouter(
    prefix="/bank-rates",
    tags=["Bank Interest Rates"],
)


@router.get("/latest", response_model=BankRateLatestOut)
def get_latest_bank_rates(
    db: SessionDep,
    bank_code: Optional[str] = Query(
        None, description="Filter by bank code (e.g. VCB, TCB)"
    ),
    term_months: Optional[int] = Query(None, description="Filter by term in months"),
    currency: str = Query("VND", description="Currency: VND or USD"),
):
    """Get the latest interest rate for each (bank_code, term_months) pair."""
    sub = (
        db.query(
            BankInterestRate.bank_code,
            BankInterestRate.term_months,
            BankInterestRate.currency,
            func.max(BankInterestRate.scraped_at).label("max_scraped"),
        )
        .filter(BankInterestRate.currency == currency)
        .group_by(
            BankInterestRate.bank_code,
            BankInterestRate.term_months,
            BankInterestRate.currency,
        )
    )
    if bank_code:
        sub = sub.filter(BankInterestRate.bank_code == bank_code.upper())
    if term_months is not None:
        sub = sub.filter(BankInterestRate.term_months == term_months)
    sub = sub.subquery()

    query = (
        db.query(BankInterestRate)
        .join(
            sub,
            (BankInterestRate.bank_code == sub.c.bank_code)
            & (BankInterestRate.term_months == sub.c.term_months)
            & (BankInterestRate.currency == sub.c.currency)
            & (BankInterestRate.scraped_at == sub.c.max_scraped),
        )
        .order_by(BankInterestRate.bank_code, BankInterestRate.term_months)
    )

    results = query.all()
    return BankRateLatestOut(count=len(results), data=results)


@router.get("/history", response_model=BankRateLatestOut)
def get_bank_rate_history(
    db: SessionDep,
    params: HistoryParamsDep,
    bank_code: Optional[str] = Query(None, description="Filter by bank code"),
    term_months: Optional[int] = Query(None, description="Filter by term in months"),
):
    """Get historical bank interest rates with optional filters and pagination."""
    query = db.query(BankInterestRate)

    if bank_code:
        query = query.filter(BankInterestRate.bank_code == bank_code.upper())
    if term_months is not None:
        query = query.filter(BankInterestRate.term_months == term_months)
    if params.start_date:
        query = query.filter(BankInterestRate.scraped_at >= params.start_date)
    if params.end_date:
        query = query.filter(BankInterestRate.scraped_at <= params.end_date)

    query = (
        query.order_by(desc(BankInterestRate.scraped_at))
        .offset(params.offset)
        .limit(params.limit)
    )
    results = query.all()
    return BankRateLatestOut(count=len(results), data=results)


@router.get("/banks/{bank_code}", response_model=BankRateOut)
def get_bank_detail(bank: ExistingBankDep):
    """Get the most recent rate record for a single bank.

    Demonstrates a chained dependency: `bank` resolves via `get_existing_bank`,
    which itself depends on `SessionDep` -> `get_db`. Unlike the optional
    `bank_code` filter on /latest and /history, this 404s if the bank doesn't exist.
    """
    return bank


@router.get("/banks", response_model=BankListOut)
def get_banks(db: SessionDep):
    """List all distinct banks with their codes and names."""
    banks = (
        db.query(
            BankInterestRate.bank_code,
            BankInterestRate.bank_name,
        )
        .distinct()
        .order_by(BankInterestRate.bank_code)
        .all()
    )
    return BankListOut(banks=[{"code": b[0], "name": b[1]} for b in banks])


@router.get("/compare", response_model=BankRateLatestOut)
def compare_bank_rates(
    db: SessionDep,
    term_months: int = Query(..., description="Deposit term in months to compare"),
    currency: str = Query("VND", description="Currency: VND or USD"),
):
    """Compare latest rates across all banks for a specific term."""
    sub = (
        db.query(
            BankInterestRate.bank_code,
            func.max(BankInterestRate.scraped_at).label("max_scraped"),
        )
        .filter(
            BankInterestRate.term_months == term_months,
            BankInterestRate.currency == currency,
        )
        .group_by(BankInterestRate.bank_code)
        .subquery()
    )

    query = (
        db.query(BankInterestRate)
        .join(
            sub,
            (BankInterestRate.bank_code == sub.c.bank_code)
            & (BankInterestRate.scraped_at == sub.c.max_scraped),
        )
        .filter(
            BankInterestRate.term_months == term_months,
            BankInterestRate.currency == currency,
        )
        .order_by(desc(BankInterestRate.interest_rate))
    )

    results = query.all()
    return BankRateLatestOut(count=len(results), data=results)


@router.post("/scrape", response_model=ScrapeResultOut)
def trigger_bank_rates_scrape():
    """Manually trigger the bank interest rate scraper."""
    try:
        count = scrape_bank_rates()
        return ScrapeResultOut(
            status="success",
            records_saved=count,
            message=f"Scraped and saved {count} bank rate records",
        )
    except Exception as exc:
        return ScrapeResultOut(
            status="error",
            records_saved=0,
            message=f"Scrape failed: {exc}",
        )
