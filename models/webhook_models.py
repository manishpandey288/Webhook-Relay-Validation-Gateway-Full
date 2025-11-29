from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class WebhookEvent(Base):
    __tablename__ = "webhook_events"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(100), index=True, nullable=True)
    event_type = Column(String(100), index=True)
    payload = Column(JSON)
    raw_body = Column(Text)  # Original raw body for HMAC verification
    signature = Column(String(255), nullable=True)
    status = Column(String(50), default="pending")  # pending, processing, delivered, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)
    retry_count = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    internal_url = Column(String(500), nullable=True)

class DeadLetterEvent(Base):
    __tablename__ = "dead_letter_events"
    
    id = Column(Integer, primary_key=True, index=True)
    webhook_event_id = Column(Integer, index=True)
    tenant_id = Column(String(100), index=True, nullable=True)
    event_type = Column(String(100))
    payload = Column(JSON)
    raw_body = Column(Text)
    failure_reason = Column(Text)
    retry_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    replayed_at = Column(DateTime, nullable=True)
    replayed = Column(Boolean, default=False)

class EventAttempt(Base):
    __tablename__ = "event_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    webhook_event_id = Column(Integer, index=True)
    attempt_number = Column(Integer)
    status = Column(String(50))  # success, failed
    response_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    attempted_at = Column(DateTime, default=datetime.utcnow)
    retry_delay = Column(Integer, nullable=True)  # seconds waited before this attempt

