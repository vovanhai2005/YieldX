import logging
import threading
from contextlib import asynccontextmanager

from dotenv import load_dotenv

# Load .env BEFORE any config imports
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.db import init_db, engine
from domains.gold import router as gold_router
from domains.bank_rates import router as bank_rates_router
from domains.forex import router as forex_router
from domains.crypto import router as crypto_router
from workers.scheduler import start_scheduler, stop_scheduler, run_initial_scrape

# ─── Logging ─────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ─── Lifespan ────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown lifecycle."""
    # Startup: ensure all tables exist
    try:
        logger.info("Creating database tables...")
        init_db()

        # Run initial scrape in a background thread so the server starts immediately
        logger.info("Starting initial data scrape in background...")
        scrape_thread = threading.Thread(target=run_initial_scrape, daemon=True)
        scrape_thread.start()

        # Start periodic scheduler
        start_scheduler()
        logger.info("Application startup complete")
    except Exception as exc:
        logger.error(f"Startup error (non-fatal, server will still run): {exc}")

    yield

    # Shutdown
    try:
        stop_scheduler()
        engine.dispose()
    except Exception:
        pass
    logger.info("Application shutdown complete")


# ─── App ─────────────────────────────────────────────────────────
app = FastAPI(
    title="YIELDX API",
    description="API theo dõi tỷ suất sinh lời các tài sản tại Việt Nam (Gold, Bank Rates, Forex, Crypto)",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ─────────────────────────────────────────────────────
app.include_router(gold_router.router)
app.include_router(bank_rates_router.router)
app.include_router(forex_router.router)
app.include_router(crypto_router.router)


# ─── Health Check ────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def health_check():
    """Root health-check endpoint."""
    return {
        "status": "healthy",
        "service": "YieldX API",
        "version": "1.0.0",
        "endpoints": {
            "gold": "/gold/latest",
            "bank_rates": "/bank-rates/latest",
            "forex": "/forex/latest",
            "crypto": "/crypto/latest",
            "docs": "/docs",
        },
    }
