from pydantic_settings import BaseSettings
import os
import sys

class Settings(BaseSettings):
    # Database - default to the Railway MySQL connection string if env not set
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:AZHMTtrJKSmuvruJHVxZeDTHpGZSEWih@mysql.railway.internal:3306/railway",
    ).strip()
    
    # Webhook Settings
    WEBHOOK_SECRET: str = "your-secret-key-change-this"
    INTERNAL_WEBHOOK_URL: str = "http://localhost:8001/internal/webhook"
    
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

    # Read raw value and strip whitespace/newlines
    _raw_db = os.getenv("DATABASE_URL", "").strip()

    # If Railway inserted a placeholder like "railway" or the value is empty,
    # fall back to a local SQLite DB for development. In production you must
    # set `DATABASE_URL` to a full connection string (mysql+pymysql://... or
    # postgresql://...)
    if _raw_db and _raw_db.lower() != "railway":
        DATABASE_URL: str = _raw_db
    else:
        # Development fallback
        DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./gateway.db").strip()

    # Webhook settings
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "your-secret-key-change-this")
    INTERNAL_WEBHOOK_URL: str = os.getenv("INTERNAL_WEBHOOK_URL", "http://localhost:8001/internal/webhook")

    # Rate limiting
    try:
        DEFAULT_RATE_LIMIT: int = int(os.getenv("DEFAULT_RATE_LIMIT", "10"))
    except ValueError:
        DEFAULT_RATE_LIMIT: int = 10
    try:
        MAX_RATE_LIMIT: int = int(os.getenv("MAX_RATE_LIMIT", "50"))
    except ValueError:
        MAX_RATE_LIMIT: int = 50

    # Retry settings
    try:
        MAX_RETRY_ATTEMPTS: int = int(os.getenv("MAX_RETRY_ATTEMPTS", "8"))
    except ValueError:
        MAX_RETRY_ATTEMPTS: int = 8
    try:
        INITIAL_RETRY_DELAY: int = int(os.getenv("INITIAL_RETRY_DELAY", "1"))
    except ValueError:
        INITIAL_RETRY_DELAY: int = 1

    # Worker settings
    try:
        WORKER_POLL_INTERVAL: int = int(os.getenv("WORKER_POLL_INTERVAL", "2"))
    except ValueError:
        WORKER_POLL_INTERVAL: int = 2

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

