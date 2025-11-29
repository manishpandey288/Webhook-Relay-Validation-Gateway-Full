from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from models.webhook_models import Base

engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autoflush=False, bind=engine)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

