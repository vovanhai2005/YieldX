"""
Forex exchange rate scraper for Vietnamese banks.

Source
──────
Vietcombank official XML feed:
https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx

The feed returns XML with <Exrate> elements containing:
  CurrencyCode, CurrencyName, Buy, Transfer, Sell
"""

import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

import httpx

from core.db import get_db_session, bulk_save
from domains.forex.models import ForexRate

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
}

VCB_XML_URL = "https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx"


def _parse_decimal(value: str | None) -> Decimal | None:
    """Parse a decimal string, returning None for empty/invalid."""
    if not value:
        return None
    cleaned = value.strip().replace(",", "")
    if not cleaned or cleaned == "-":
        return None
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def _scrape_vietcombank() -> list[dict]:
    """Scrape exchange rates from Vietcombank XML feed."""
    rows: list[dict] = []
    now = datetime.now(timezone.utc)

    try:
        resp = httpx.get(
            VCB_XML_URL, headers=HEADERS, timeout=15, follow_redirects=True
        )
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("Vietcombank XML scrape failed: %s", exc)
        return rows

    try:
        root = ET.fromstring(resp.text)
    except ET.ParseError as exc:
        logger.warning("Vietcombank XML parse failed: %s", exc)
        return rows

    # The XML structure: <ExrateList><DateTime>...</DateTime><Exrate CurrencyCode="..." .../>...</ExrateList>
    for exrate in root.iter("Exrate"):
        currency_code = exrate.get("CurrencyCode", "").strip()
        currency_name = exrate.get("CurrencyName", "").strip()
        buy_cash = _parse_decimal(exrate.get("Buy"))
        buy_transfer = _parse_decimal(exrate.get("Transfer"))
        sell = _parse_decimal(exrate.get("Sell"))

        if not currency_code:
            continue

        # Skip if all rates are empty
        if buy_cash is None and buy_transfer is None and sell is None:
            continue

        rows.append(
            {
                "currency_code": currency_code,
                "currency_name": currency_name or currency_code,
                "buy_cash": buy_cash,
                "buy_transfer": buy_transfer,
                "sell": sell,
                "source": "Vietcombank",
                "scraped_at": now,
            }
        )

    logger.info("Vietcombank: scraped %d forex rate rows", len(rows))
    return rows


def scrape_forex() -> int:
    """Run forex scrapers and persist results. Returns total rows saved."""
    rows = _scrape_vietcombank()

    if not rows:
        logger.warning("Forex scrape returned 0 rows")
        return 0

    with get_db_session() as db:
        bulk_save(db, ForexRate, rows)

    logger.info("Forex: saved %d total rows", len(rows))
    return len(rows)
