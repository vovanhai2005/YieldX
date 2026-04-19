"""
Application configuration loaded from environment variables.

Set these variables in your environment or a .env file:
    DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
    DB_POOL_SIZE, DB_MAX_OVERFLOW, DB_POOL_TIMEOUT, DB_POOL_RECYCLE
    DB_ECHO, DEBUG
"""

import os
from dataclasses import dataclass, field


@dataclass
class DatabaseSettings:
    """PostgreSQL connection and pool configuration."""

    host: str = field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("DB_PORT", "5432")))
    user: str = field(default_factory=lambda: os.getenv("DB_USER", "yieldx"))
    password: str = field(default_factory=lambda: os.getenv("DB_PASSWORD", "yieldx"))
    name: str = field(default_factory=lambda: os.getenv("DB_NAME", "yieldx"))

    # Connection pool tuning
    pool_size: int = field(
        default_factory=lambda: int(os.getenv("DB_POOL_SIZE", "10"))
    )
    max_overflow: int = field(
        default_factory=lambda: int(os.getenv("DB_MAX_OVERFLOW", "20"))
    )
    pool_timeout: int = field(
        default_factory=lambda: int(os.getenv("DB_POOL_TIMEOUT", "30"))
    )
    pool_recycle: int = field(
        default_factory=lambda: int(os.getenv("DB_POOL_RECYCLE", "1800"))
    )
    echo: bool = field(
        default_factory=lambda: os.getenv("DB_ECHO", "false").lower() == "true"
    )

    @property
    def url(self) -> str:
        """Build PostgreSQL connection URL for psycopg2."""
        return (
            f"postgresql+psycopg2://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )


@dataclass
class Settings:
    """Root application settings."""

    app_name: str = "YieldX"
    debug: bool = field(
        default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true"
    )
    database: DatabaseSettings = field(default_factory=DatabaseSettings)


settings = Settings()
