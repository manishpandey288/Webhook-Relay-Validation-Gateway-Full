from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from datetime import datetime

from db.database import get_db
from models.webhook_models import WebhookEvent, DeadLetterEvent, EventAttempt

router = APIRouter()

@router.post("/replay/{event_id}")
async def replay_event(event_id: int, db: Session = Depends(get_db)):
    """
    STEP 8: Replay event from dead-letter queue
    """
    # Get dead-letter event
    dead_letter = db.query(DeadLetterEvent).filter(
        DeadLetterEvent.id == event_id
    ).first()
    
    if not dead_letter:
        # Try to get from webhook_events if it's a regular event
        event = db.query(WebhookEvent).filter(WebhookEvent.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Reset event and requeue
        event.status = "pending"
        event.retry_count = 0
        event.last_error = None
        db.commit()
        db.refresh(event)
        
        # Event is now pending, worker will pick it up
        return {"status": "replayed", "event_id": event.id}
    
    # Create new webhook event from dead-letter
    new_event = WebhookEvent(
        tenant_id=dead_letter.tenant_id,
        event_type=dead_letter.event_type,
        payload=dead_letter.payload,
        raw_body=dead_letter.raw_body,
        status="pending",
        retry_count=0
    )
    db.add(new_event)
    
    # Mark dead-letter as replayed
    dead_letter.replayed = True
    dead_letter.replayed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(new_event)
    
    # Event is now pending, worker will pick it up
    return {"status": "replayed", "event_id": new_event.id, "original_id": dead_letter.id}

@router.get("/metrics")
async def get_metrics(
    tenant_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    STEP 10: Get metrics and logs
    """
    query = db.query(WebhookEvent)
    if tenant_id:
        query = query.filter(WebhookEvent.tenant_id == tenant_id)
    
    total_events = query.count()
    delivered = query.filter(WebhookEvent.status == "delivered").count()
    failed = query.filter(WebhookEvent.status == "failed").count()
    pending = query.filter(WebhookEvent.status == "pending").count()
    processing = query.filter(WebhookEvent.status == "processing").count()
    
    # Average retry count
    avg_retries = db.query(func.avg(WebhookEvent.retry_count)).scalar() or 0
    
    # Dead-letter count
    dl_query = db.query(DeadLetterEvent)
    if tenant_id:
        dl_query = dl_query.filter(DeadLetterEvent.tenant_id == tenant_id)
    dead_letter_count = dl_query.count()
    
    # Recent events
    recent_events = query.order_by(desc(WebhookEvent.created_at)).limit(10).all()
    
    return {
        "summary": {
            "total_events": total_events,
            "delivered": delivered,
            "failed": failed,
            "pending": pending,
            "processing": processing,
            "dead_letter": dead_letter_count,
            "average_retries": round(avg_retries, 2),
            "success_rate": round((delivered / total_events * 100) if total_events > 0 else 0, 2)
        },
        "recent_events": [
            {
                "id": e.id,
                "tenant_id": e.tenant_id,
                "event_type": e.event_type,
                "status": e.status,
                "retry_count": e.retry_count,
                "created_at": e.created_at.isoformat() if e.created_at else None
            }
            for e in recent_events
        ]
    }

@router.get("/events/{event_id}/attempts")
async def get_event_attempts(event_id: int, db: Session = Depends(get_db)):
    """
    STEP 10: Get attempt history for an event
    """
    event = db.query(WebhookEvent).filter(WebhookEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    attempts = db.query(EventAttempt).filter(
        EventAttempt.webhook_event_id == event_id
    ).order_by(EventAttempt.attempt_number).all()
    
    return {
        "event_id": event_id,
        "status": event.status,
        "retry_count": event.retry_count,
        "attempts": [
            {
                "attempt_number": a.attempt_number,
                "status": a.status,
                "response_code": a.response_code,
                "error_message": a.error_message,
                "retry_delay": a.retry_delay,
                "attempted_at": a.attempted_at.isoformat() if a.attempted_at else None
            }
            for a in attempts
        ]
    }

@router.get("/dead-letters")
async def get_dead_letters(
    tenant_id: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get dead-letter events"""
    query = db.query(DeadLetterEvent)
    if tenant_id:
        query = query.filter(DeadLetterEvent.tenant_id == tenant_id)
    
    dead_letters = query.order_by(desc(DeadLetterEvent.created_at)).limit(limit).all()
    
    return {
        "dead_letters": [
            {
                "id": dl.id,
                "webhook_event_id": dl.webhook_event_id,
                "tenant_id": dl.tenant_id,
                "event_type": dl.event_type,
                "failure_reason": dl.failure_reason,
                "retry_count": dl.retry_count,
                "replayed": dl.replayed,
                "created_at": dl.created_at.isoformat() if dl.created_at else None
            }
            for dl in dead_letters
        ]
    }

@router.get("/events")
async def list_events(
    tenant_id: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List recent events"""
    query = db.query(WebhookEvent)
    if tenant_id:
        query = query.filter(WebhookEvent.tenant_id == tenant_id)
    
    events = query.order_by(desc(WebhookEvent.created_at)).limit(limit).all()
    
    return {
        "events": [
            {
                "id": e.id,
                "tenant_id": e.tenant_id,
                "event_type": e.event_type,
                "status": e.status,
                "retry_count": e.retry_count,
                "created_at": e.created_at.isoformat() if e.created_at else None,
                "delivered_at": e.delivered_at.isoformat() if e.delivered_at else None
            }
            for e in events
        ]
    }

