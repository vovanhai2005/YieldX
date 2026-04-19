"""
Cryptocurrency price scraper using the CoinGecko public API.

Source
──────
CoinGecko /coins/markets endpoint (free, no API key required):
https://api.coingecko.com/api/v3/coins/markets

Returns top cryptocurrencies with price, market cap, volume, and 24h change
in both USD and VND.
"""

import logging
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

import httpx

from core.db import get_db_session, bulk_save
from domains.crypto.models import CryptoPrice

logger = logging.getLogger(__name__)

COINGECKO_MARKETS_URL = "https://api.coingecko.com/api/v3/coins/markets"

# Top coins to track (CoinGecko IDs)
DEFAULT_COINS = [
    "bitcoin",
    "ethereum",
    "tether",
    "binancecoin",
    "solana",
    "ripple",
    "usd-coin",
    "cardano",
    "dogecoin",
    "tron",
    "polkadot",
    "chainlink",
    "avalanche-2",
    "toncoin",
    "shiba-inu",
    "stellar",
    "sui",
    "near",
    "aptos",
    "pepe",
]


def _safe_decimal(value) -> Decimal | None:
    """Safely convert a value to Decimal."""
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _fetch_coingecko_markets(vs_currency: str = "usd", per_page: int = 20) -> list[dict]:
    """Fetch market data from CoinGecko."""
    params = {
        "vs_currency": vs_currency,
        "ids": ",".join(DEFAULT_COINS),
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "24h",
    }

    try:
        resp = httpx.get(
            COINGECKO_MARKETS_URL,
            params=params,
            timeout=15,
            follow_redirects=True,
        )
        resp.raise_for_status()
        return resp.json()
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("CoinGecko %s fetch failed: %s", vs_currency, exc)
        return []


def _scrape_coingecko() -> list[dict]:
    """Scrape cryptocurrency prices from CoinGecko."""
    rows: list[dict] = []
    now = datetime.now(timezone.utc)

    # Fetch USD data (includes market cap, volume, change)
    usd_data = _fetch_coingecko_markets(vs_currency="usd")
    # Fetch VND prices separately
    vnd_data = _fetch_coingecko_markets(vs_currency="vnd")

    # Build VND price lookup
    vnd_prices: dict[str, Decimal | None] = {}
    for coin in vnd_data:
        coin_id = coin.get("id", "")
        vnd_prices[coin_id] = _safe_decimal(coin.get("current_price"))

    for coin in usd_data:
        coin_id = coin.get("id", "")
        symbol = coin.get("symbol", "").upper()
        name = coin.get("name", "")
        price_usd = _safe_decimal(coin.get("current_price"))

        if price_usd is None:
            continue

        rows.append(
            {
                "symbol": symbol,
                "name": name,
                "price_usd": price_usd,
                "price_vnd": vnd_prices.get(coin_id),
                "market_cap_usd": _safe_decimal(coin.get("market_cap")),
                "volume_24h_usd": _safe_decimal(coin.get("total_volume")),
                "change_24h_pct": _safe_decimal(coin.get("price_change_percentage_24h")),
                "source": "CoinGecko",
                "scraped_at": now,
            }
        )

    logger.info("CoinGecko: scraped %d crypto price rows", len(rows))
    return rows


def scrape_crypto() -> int:
    """Run crypto scrapers and persist results. Returns total rows saved."""
    rows = _scrape_coingecko()

    if not rows:
        logger.warning("Crypto scrape returned 0 rows")
        return 0

    with get_db_session() as db:
        bulk_save(db, CryptoPrice, rows)

    logger.info("Crypto: saved %d total rows", len(rows))
    return len(rows)
