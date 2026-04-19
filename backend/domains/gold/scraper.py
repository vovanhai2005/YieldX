"""
Gold price scraper for Vietnamese gold dealers.

Sources
───────
• SJC  — https://sjc.com.vn/giavang/textContent.php  (HTML fragment)
• DOJI — https://giavang.doji.vn/                      (HTML page)

Each scraper function returns a list[dict] matching GoldPrice model columns.
"""

import logging
import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

import httpx
from bs4 import BeautifulSoup

from core.db import get_db_session, bulk_save
from domains.gold.models import GoldPrice

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
}

# ─── Helpers ────────────────────────────────────────────────────

def _parse_price(text: str) -> Decimal | None:
    """Convert a Vietnamese price string like '82,000,000' or '82.000.000' to Decimal."""
    if not text:
        return None
    cleaned = re.sub(r"[^\d]", "", text.strip())
    if not cleaned:
        return None
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


# ─── SJC Scraper ─────────────────────────────────────────────────


def _scrape_sjc() -> list[dict]:
    """Scrape gold prices from SJC website."""
    url = "https://sjc.com.vn/giavang/textContent.php"
    rows: list[dict] = []
    now = datetime.now(timezone.utc)

    try:
        resp = httpx.get(url, headers=HEADERS, timeout=15, follow_redirects=True)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("SJC scrape failed: %s", exc)
        return rows

    soup = BeautifulSoup(resp.text, "lxml")

    # SJC page has a table with rows: [product_type, buy_price, sell_price]
    for tr in soup.select("tr"):
        cells = tr.find_all("td")
        if len(cells) < 3:
            continue

        product_type = cells[0].get_text(strip=True)
        if not product_type or product_type.lower() in ("loại", "type", ""):
            continue

        buy_price = _parse_price(cells[1].get_text(strip=True))
        sell_price = _parse_price(cells[2].get_text(strip=True))

        if buy_price is None and sell_price is None:
            continue

        rows.append(
            {
                "brand": "SJC",
                "product_type": product_type,
                "buy_price": buy_price,
                "sell_price": sell_price,
                "source": "https://sjc.com.vn",
                "scraped_at": now,
            }
        )

    logger.info("SJC: scraped %d gold price rows", len(rows))
    return rows


# ─── DOJI Scraper ────────────────────────────────────────────────


def _scrape_doji() -> list[dict]:
    """Scrape gold prices from DOJI website."""
    url = "https://giavang.doji.vn/"
    rows: list[dict] = []
    now = datetime.now(timezone.utc)

    try:
        resp = httpx.get(url, headers=HEADERS, timeout=15, follow_redirects=True)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("DOJI scrape failed: %s", exc)
        return rows

    soup = BeautifulSoup(resp.text, "lxml")

    # DOJI table rows
    for tr in soup.select("table tr"):
        cells = tr.find_all("td")
        if len(cells) < 3:
            continue

        product_type = cells[0].get_text(strip=True)
        if not product_type or "loại" in product_type.lower():
            continue

        buy_price = _parse_price(cells[1].get_text(strip=True))
        sell_price = _parse_price(cells[2].get_text(strip=True))

        if buy_price is None and sell_price is None:
            continue

        rows.append(
            {
                "brand": "DOJI",
                "product_type": product_type,
                "buy_price": buy_price,
                "sell_price": sell_price,
                "source": "https://giavang.doji.vn",
                "scraped_at": now,
            }
        )

    logger.info("DOJI: scraped %d gold price rows", len(rows))
    return rows


# ─── Public API ──────────────────────────────────────────────────


def scrape_gold() -> int:
    """Run all gold scrapers and persist results. Returns total rows saved."""
    all_rows: list[dict] = []
    all_rows.extend(_scrape_sjc())
    all_rows.extend(_scrape_doji())

    if not all_rows:
        logger.warning("Gold scrape returned 0 rows from all sources")
        return 0

    with get_db_session() as db:
        bulk_save(db, GoldPrice, all_rows)

    logger.info("Gold: saved %d total rows", len(all_rows))
    return len(all_rows)
