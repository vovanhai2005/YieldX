"""
SQLAlchemy database engine, session management, and base model definitions.

Architecture notes for time-series financial data:
─────────────────────────────────────────────────
• All domain tables are APPEND-ONLY (no UPDATEs) → uses TimeSeriesMixin (created_at only).
• Primary keys are BigInteger auto-increment for sequential write locality.
• Every table has a composite index on (identifier, scraped_at DESC) to serve
  the dominant query pattern: "latest N records for asset X".
• A secondary index on scraped_at alone supports cross-asset time-range scans.
• pool_pre_ping=True ensures stale connections are recycled transparently.
• get_db() is the FastAPI Depends() pathway; get_db_session() is a context
  manager for background workers / scrapers that auto-commits or rolls back.
"""

from datetime import datetime
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, DateTime, func, insert
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker,
    Session,
)

from core.config import settings

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Engine & Session Factory
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

engine = create_engine(
    settings.database.url,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    pool_timeout=settings.database.pool_timeout,
    pool_recycle=settings.database.pool_recycle,
    pool_pre_ping=True,
    echo=settings.database.echo,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Declarative Base & Mixins
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""

    pass


class TimeSeriesMixin:
    """Mixin for append-only time-series tables.

    Time-series records are never updated after insertion,
    so only `created_at` is tracked (no `updated_at`).
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Row insertion timestamp (server-side)",
    )


class TimestampMixin(TimeSeriesMixin):
    """Mixin for mutable tables that need update tracking.

    Extends TimeSeriesMixin with an `updated_at` column that
    auto-updates on every row modification.
    """

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last modification timestamp",
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Session Dependencies
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency — yields a session, closes on request teardown.

    Usage:
        @router.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager for workers / scrapers outside the FastAPI request cycle.

    Auto-commits on clean exit, auto-rollbacks on exception.

    Usage:
        with get_db_session() as db:
            db.add_all(records)
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Bulk Insert Helper
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def bulk_save(db: Session, model: type[Base], rows: list[dict]) -> None:
    """High-performance bulk insert using Core INSERT (bypasses ORM unit-of-work).

    Ideal for scraper ingestion where thousands of rows are inserted per batch.

    Args:
        db:    Active SQLAlchemy session.
        model: ORM model class (e.g. GoldPrice).
        rows:  List of dicts whose keys match column names.
    """
    if not rows:
        return
    db.execute(insert(model), rows)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Schema Lifecycle
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def init_db() -> None:
    """Create all tables registered with Base.metadata.

    Imports every domain model module so that its table definitions
    are registered before calling CREATE TABLE.
    """
    import domains.gold.models  # noqa: F401
    import domains.bank_rates.models  # noqa: F401
    import domains.forex.models  # noqa: F401
    import domains.crypto.models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """Drop all tables. ⚠️  Destructive — never call in production."""
    Base.metadata.drop_all(bind=engine)
