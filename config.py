from pydantic_settings import BaseSettings
from pydantic import field_validator, Field
import os
import sys


def _get_database_url() -> str:
    """Compute DATABASE_URL from env vars, cleaning up newlines and normalizing scheme."""
    raw_db = os.getenv("DATABASE_URL", "")
    
    # Remove newlines and whitespace
    raw_db = raw_db.replace("\n", "").replace("\r", "").strip()

    if raw_db:
        # Convert mysql:// to mysql+pymysql:// for SQLAlchemy + PyMySQL
        if raw_db.startswith("mysql://"):
            return raw_db.replace("mysql://", "mysql+pymysql://", 1)
        else:
            return raw_db
    else:
        # If no DATABASE_URL, use SQLite fallback
        return "sqlite:///./gateway.db"


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Database connection URL (computed from _get_database_url)
    DATABASE_URL: str = Field(default_factory=_get_database_url)

    # Webhook Settings
    WEBHOOK_SECRET: str = "your-secret-key-change-this"
    INTERNAL_WEBHOOK_URL: str = "https://webhook-relay-validation-gateway-full-production.up.railway.app/internal/webhook"

    # Rate Limiting
    DEFAULT_RATE_LIMIT: int = 10  # events per second per tenant
    MAX_RATE_LIMIT: int = 50

    # Retry Settings
    MAX_RETRY_ATTEMPTS: int = 8
    INITIAL_RETRY_DELAY: int = 1  # seconds

    # Worker Settings
    WORKER_POLL_INTERVAL: int = 2  # seconds between polling for pending events

    class Config:
        env_file = ".env"
        case_sensitive = True



settings = Settings()

# Quick validation: if DATABASE_URL still looks like a placeholder, warn
db_val = (settings.DATABASE_URL or "").strip()
if not db_val:
    print("Warning: DATABASE_URL is empty; using SQLite fallback.", file=sys.stderr)
elif db_val.lower() == "railway":
    print(
        "ERROR: DATABASE_URL is set to the placeholder 'railway'.\n"
        "Please set the full DATABASE_URL in Railway variables, e.g.\n"
        "mysql+pymysql://user:password@host:port/dbname\n",
        file=sys.stderr,
    )

