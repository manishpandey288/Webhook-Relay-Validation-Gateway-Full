from pydantic_settings import BaseSettings
import envparse

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = envparse.env("DATABASE_URL")
    
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

settings = Settings()

