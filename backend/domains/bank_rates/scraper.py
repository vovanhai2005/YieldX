"""
Bank interest rate scraper for Vietnamese banks.

Strategy
────────
Since there's no single reliable free API for Vietnamese bank deposit rates,
we maintain a curated mapping of top banks and their publicly listed rates.
The scraper fetches from aggregator pages (e.g. webgia.com) or falls back
to a built-in snapshot of typical Vietnamese bank rates that can be updated
periodically.

This scraper uses the webgia.com interest rate page as the primary source.
"""

import logging
import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

import httpx
from bs4 import BeautifulSoup

from core.db import get_db_session, bulk_save
from domains.bank_rates.models import BankInterestRate

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
}

# Vietnamese bank code → full name mapping
BANK_MAP = {
    "VCB": "Vietcombank",
    "BIDV": "BIDV",
    "AGR": "Agribank",
    "CTG": "VietinBank",
    "TCB": "Techcombank",
    "MBB": "MB Bank",
    "VPB": "VPBank",
    "ACB": "ACB",
    "STB": "Sacombank",
    "HDB": "HDBank",
    "TPB": "TPBank",
    "MSB": "MSB",
    "SHB": "SHB",
    "EIB": "Eximbank",
    "LPB": "LienVietPostBank",
    "OCB": "OCB",
    "NAB": "Nam A Bank",
    "BAB": "Bac A Bank",
    "VIB": "VIB",
    "SSB": "SeABank",
}

# Reverse lookup
NAME_TO_CODE = {}
for code, name in BANK_MAP.items():
    NAME_TO_CODE[name.lower()] = code
    # Also map partial names
    NAME_TO_CODE[code.lower()] = code

# Standard term months to look for
STANDARD_TERMS = [1, 3, 6, 9, 12, 13, 18, 24, 36]


def _parse_rate(text: str) -> Decimal | None:
    """Convert a rate string like '5.50' or '5,50' to Decimal."""
    if not text:
        return None
    cleaned = text.strip().replace(",", ".").replace("%", "").strip()
    if not cleaned or cleaned == "-":
        return None
    try:
        val = Decimal(cleaned)
        # Sanity check: rates should be between 0 and 20%
        if val < 0 or val > 20:
            return None
        return val
    except InvalidOperation:
        return None


def _find_bank_code(name: str) -> str | None:
    """Try to match a bank name to our known bank codes."""
    lower = name.lower().strip()
    # Direct match
    if lower in NAME_TO_CODE:
        return NAME_TO_CODE[lower]
    # Partial match
    for known_name, code in NAME_TO_CODE.items():
        if known_name in lower or lower in known_name:
            return code
    return None


def _scrape_webgia() -> list[dict]:
    """Scrape bank interest rates from webgia.com."""
    url = "https://webgia.com/lai-suat/"
    rows: list[dict] = []
    now = datetime.now(timezone.utc)

    try:
        resp = httpx.get(url, headers=HEADERS, timeout=15, follow_redirects=True)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("webgia.com scrape failed: %s", exc)
        return rows

    soup = BeautifulSoup(resp.text, "lxml")

    # webgia.com typically has a table with bank names in rows and terms in columns
    tables = soup.find_all("table")
    for table in tables:
        # Try to find header row to identify term columns
        header_row = table.find("tr")
        if not header_row:
            continue

        headers = [th.get_text(strip=True) for th in header_row.find_all(["th", "td"])]
        if len(headers) < 3:
            continue

        # Parse term months from headers (e.g. "1 tháng", "3 tháng", "12 tháng")
        term_indices: list[tuple[int, int]] = []  # (col_index, term_months)
        for i, header in enumerate(headers):
            match = re.search(r"(\d+)", header)
            if match:
                term = int(match.group(1))
                if term in STANDARD_TERMS or term <= 60:
                    term_indices.append((i, term))

        if not term_indices:
            continue

        # Parse data rows
        for tr in table.find_all("tr")[1:]:
            cells = tr.find_all(["td", "th"])
            if len(cells) < 2:
                continue

            bank_name_raw = cells[0].get_text(strip=True)
            bank_code = _find_bank_code(bank_name_raw)
            if not bank_code:
                continue

            bank_name = BANK_MAP.get(bank_code, bank_name_raw)

            for col_idx, term_months in term_indices:
                if col_idx >= len(cells):
                    continue
                rate = _parse_rate(cells[col_idx].get_text(strip=True))
                if rate is None:
                    continue

                rows.append(
                    {
                        "bank_code": bank_code,
                        "bank_name": bank_name,
                        "term_months": term_months,
                        "interest_rate": rate,
                        "rate_type": "counter",
                        "currency": "VND",
                        "min_deposit": None,
                        "source": "https://webgia.com/lai-suat/",
                        "scraped_at": now,
                    }
                )

    logger.info("webgia.com: scraped %d bank rate rows", len(rows))
    return rows


def _fallback_rates() -> list[dict]:
    """Provide a baseline set of Vietnamese bank rates when scraping fails.

    These are representative rates as of Q1 2026 and will be refreshed
    each time a real scrape succeeds.
    """
    now = datetime.now(timezone.utc)
    # Representative deposit rates (% per year) for Vietnamese banks
    # Format: (bank_code, {term_months: rate})
    rate_data = [
        ("VCB", {1: 1.6, 3: 2.0, 6: 3.0, 9: 3.0, 12: 4.7, 18: 4.7, 24: 4.7, 36: 4.7}),
        ("BIDV", {1: 1.6, 3: 2.0, 6: 3.0, 9: 3.0, 12: 4.7, 18: 4.7, 24: 4.7, 36: 4.7}),
        ("AGR", {1: 1.6, 3: 2.0, 6: 3.0, 9: 3.0, 12: 4.7, 18: 4.7, 24: 4.7, 36: 4.7}),
        ("CTG", {1: 1.6, 3: 2.0, 6: 3.0, 9: 3.0, 12: 4.7, 18: 4.7, 24: 4.7, 36: 4.7}),
        ("TCB", {1: 2.8, 3: 3.2, 6: 4.8, 9: 4.8, 12: 5.4, 18: 5.5, 24: 5.5, 36: 5.5}),
        ("MBB", {1: 2.9, 3: 3.4, 6: 4.5, 9: 4.5, 12: 5.0, 18: 5.1, 24: 5.1, 36: 5.1}),
        ("VPB", {1: 3.1, 3: 3.6, 6: 5.1, 9: 5.2, 12: 5.6, 18: 5.7, 24: 5.7, 36: 5.7}),
        ("ACB", {1: 2.5, 3: 2.8, 6: 4.2, 9: 4.3, 12: 4.9, 18: 5.0, 24: 5.0, 36: 5.0}),
        ("STB", {1: 2.7, 3: 3.1, 6: 4.6, 9: 4.7, 12: 5.2, 18: 5.3, 24: 5.3, 36: 5.3}),
        ("HDB", {1: 2.9, 3: 3.3, 6: 4.8, 9: 5.0, 12: 5.5, 18: 5.6, 24: 5.6, 36: 5.6}),
        ("TPB", {1: 2.8, 3: 3.3, 6: 4.9, 9: 5.0, 12: 5.5, 18: 5.6, 24: 5.6, 36: 5.6}),
        ("MSB", {1: 3.0, 3: 3.5, 6: 5.0, 9: 5.1, 12: 5.5, 18: 5.6, 24: 5.6, 36: 5.6}),
        ("SHB", {1: 2.8, 3: 3.2, 6: 4.7, 9: 4.8, 12: 5.3, 18: 5.4, 24: 5.4, 36: 5.4}),
        ("EIB", {1: 2.9, 3: 3.4, 6: 4.9, 9: 5.0, 12: 5.4, 18: 5.5, 24: 5.5, 36: 5.5}),
        ("VIB", {1: 2.7, 3: 3.1, 6: 4.6, 9: 4.7, 12: 5.2, 18: 5.3, 24: 5.3, 36: 5.3}),
    ]

    rows: list[dict] = []
    for bank_code, rates in rate_data:
        bank_name = BANK_MAP.get(bank_code, bank_code)
        for term_months, rate in rates.items():
            rows.append(
                {
                    "bank_code": bank_code,
                    "bank_name": bank_name,
                    "term_months": term_months,
                    "interest_rate": Decimal(str(rate)),
                    "rate_type": "counter",
                    "currency": "VND",
                    "min_deposit": None,
                    "source": "fallback_baseline",
                    "scraped_at": now,
                }
            )

    logger.info("Fallback: generated %d baseline bank rate rows", len(rows))
    return rows


def scrape_bank_rates() -> int:
    """Run bank rate scrapers and persist results. Returns total rows saved."""
    rows = _scrape_webgia()

    if not rows:
        logger.warning("Web scrape returned 0 rows, using fallback rates")
        rows = _fallback_rates()

    if not rows:
        return 0

    with get_db_session() as db:
        bulk_save(db, BankInterestRate, rows)

    logger.info("Bank rates: saved %d total rows", len(rows))
    return len(rows)
