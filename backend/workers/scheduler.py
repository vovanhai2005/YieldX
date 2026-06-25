"""
Background job scheduler for periodic data scraping.

Uses APScheduler to run scrapers at configurable intervals.
Integrated into FastAPI lifespan for clean start/stop.

Schedule
────────
• Gold prices   — every 15 minutes
• Bank rates    — every 6 hours
• Forex rates   — every 30 minutes
• Crypto prices — every 10 minutes
"""

import logging
import threading

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(
    job_defaults={
        "coalesce": True,  # If multiple runs are missed, only run once
        "max_instances": 1,  # Never run the same job concurrently
        "misfire_grace_time": 60,
    }
)

_started = False
_lock = threading.Lock()


def _run_gold_scraper():
    """Wrapper to run gold scraper with error handling."""
    try:
        from domains.gold.scraper import scrape_gold

        count = scrape_gold()
        logger.info("[Scheduler] Gold scrape completed: %d records", count)
    except Exception as exc:
        logger.error("[Scheduler] Gold scrape failed: %s", exc)


def _run_bank_rates_scraper():
    """Wrapper to run bank rates scraper with error handling."""
    try:
        from domains.bank_rates.scraper import scrape_bank_rates

        count = scrape_bank_rates()
        logger.info("[Scheduler] Bank rates scrape completed: %d records", count)
    except Exception as exc:
        logger.error("[Scheduler] Bank rates scrape failed: %s", exc)


def _run_forex_scraper():
    """Wrapper to run forex scraper with error handling."""
    try:
        from domains.forex.scraper import scrape_forex

        count = scrape_forex()
        logger.info("[Scheduler] Forex scrape completed: %d records", count)
    except Exception as exc:
        logger.error("[Scheduler] Forex scrape failed: %s", exc)


def _run_crypto_scraper():
    """Wrapper to run crypto scraper with error handling."""
    try:
        from domains.crypto.scraper import scrape_crypto

        count = scrape_crypto()
        logger.info("[Scheduler] Crypto scrape completed: %d records", count)
    except Exception as exc:
        logger.error("[Scheduler] Crypto scrape failed: %s", exc)


def start_scheduler():
    """Register all scraping jobs and start the scheduler."""
    global _started
    with _lock:
        if _started:
            return
        _started = True

    # Gold prices — every 15 minutes
    scheduler.add_job(
        _run_gold_scraper,
        trigger=IntervalTrigger(minutes=15),
        id="gold_scraper",
        name="Gold Price Scraper",
        replace_existing=True,
    )

    # Bank interest rates — every 6 hours
    scheduler.add_job(
        _run_bank_rates_scraper,
        trigger=IntervalTrigger(hours=6),
        id="bank_rates_scraper",
        name="Bank Interest Rate Scraper",
        replace_existing=True,
    )

    # Forex exchange rates — every 30 minutes
    scheduler.add_job(
        _run_forex_scraper,
        trigger=IntervalTrigger(minutes=30),
        id="forex_scraper",
        name="Forex Exchange Rate Scraper",
        replace_existing=True,
    )

    # Crypto prices — every 10 minutes
    scheduler.add_job(
        _run_crypto_scraper,
        trigger=IntervalTrigger(minutes=10),
        id="crypto_scraper",
        name="Crypto Price Scraper",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("[Scheduler] Started with 4 jobs")


def run_initial_scrape():
    """Run all scrapers once at startup to populate the database."""
    logger.info("[Scheduler] Running initial scrape for all domains...")
    _run_gold_scraper()
    _run_bank_rates_scraper()
    _run_forex_scraper()
    _run_crypto_scraper()
    logger.info("[Scheduler] Initial scrape complete")


def stop_scheduler():
    """Gracefully shut down the scheduler."""
    global _started
    with _lock:
        if not _started:
            return
        _started = False
    scheduler.shutdown(wait=False)
    logger.info("[Scheduler] Stopped")
