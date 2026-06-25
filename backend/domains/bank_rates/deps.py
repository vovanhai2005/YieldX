"""
Domain-specific dependencies for the Bank Interest Rates domain.
"""

from typing import Annotated

from fastapi import Depends, HTTPException

from core.db import SessionDep
from domains.bank_rates.models import BankInterestRate


def get_existing_bank(bank_code: str, db: SessionDep) -> BankInterestRate:
    """Chained dependency: depends on SessionDep, which itself depends on get_db.

    Resolves `bank_code` to a real row and 404s if it doesn't exist, so route
    handlers receive an already-validated record instead of a raw string they'd
    have to re-query and re-check themselves.
    """
    bank = (
        db.query(BankInterestRate)
        .filter(BankInterestRate.bank_code == bank_code.upper())
        .first()
    )
    if bank is None:
        raise HTTPException(status_code=404, detail=f"Bank '{bank_code}' not found")
    return bank


ExistingBankDep = Annotated[BankInterestRate, Depends(get_existing_bank)]
