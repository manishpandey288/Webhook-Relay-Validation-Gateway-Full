"""
Simple background worker for processing webhook events
Uses asyncio to poll database and process events
"""
import asyncio
import httpx
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.webhook_models import WebhookEvent, DeadLetterEvent, EventAttempt
from config import settings
from datetime import datetime

class EventWorker:
    def __init__(self):
        self.running = False
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def process_event(self, event_id: int):
        """Process a single webhook event"""
        db = SessionLocal()
        try:
            # Get event from database
            event = db.query(WebhookEvent).filter(WebhookEvent.id == event_id).first()
            if not event:
                return
            
            # Skip if already processed
            if event.status in ["delivered", "failed"]:
                return
            
            # Update status to processing
            event.status = "processing"
            db.commit()
            
            # Forward to internal URL
            try:
                response = await self.client.post(
                    event.internal_url or settings.INTERNAL_WEBHOOK_URL,
                    json=event.payload
                )
                
                # Record attempt
                attempt = EventAttempt(
                    webhook_event_id=event_id,
                    attempt_number=event.retry_count + 1,
                    status="success" if response.is_success else "failed",
                    response_code=response.status_code,
                    response_body=response.text[:1000]
                )
                db.add(attempt)
                
                if response.is_success:
                    # Success!
                    event.status = "delivered"
                    event.delivered_at = datetime.utcnow()
                    db.commit()
                    return
                else:
                    # Failed - will retry
                    event.last_error = f"HTTP {response.status_code}: {response.text[:500]}"
                    raise Exception(f"HTTP {response.status_code}")
                    
            except Exception as e:
                # Record failed attempt
                attempt = EventAttempt(
                    webhook_event_id=event_id,
                    attempt_number=event.retry_count + 1,
                    status="failed",
                    error_message=str(e)[:1000]
                )
                db.add(attempt)
                
                event.retry_count += 1
                event.last_error = str(e)[:500]
                
                # Exponential backoff retry
                if event.retry_count < settings.MAX_RETRY_ATTEMPTS:
                    # Calculate delay: 1s, 2s, 4s, 8s, 16s, 32s, 64s, 128s
                    delay = settings.INITIAL_RETRY_DELAY * (2 ** (event.retry_count - 1))
                    attempt.retry_delay = delay
                    event.status = "pending"  # Reset to pending for retry
                    db.commit()
                    
                    # Schedule retry
                    await asyncio.sleep(delay)
                    await self.process_event(event_id)
                else:
                    # Move to dead-letter queue
                    event.status = "failed"
                    db.commit()
                    
                    dead_letter = DeadLetterEvent(
                        webhook_event_id=event_id,
                        tenant_id=event.tenant_id,
                        event_type=event.event_type,
                        payload=event.payload,
                        raw_body=event.raw_body,
                        failure_reason=str(e)[:1000],
                        retry_count=event.retry_count
                    )
                    db.add(dead_letter)
                    db.commit()
        
        finally:
            db.close()
    
    async def worker_loop(self):
        """Main worker loop that polls for pending events"""
        self.running = True
        print("Event worker started")
        
        while self.running:
            try:
                db = SessionLocal()
                try:
                    # Get pending events (limit to 10 at a time)
                    pending_events = db.query(WebhookEvent).filter(
                        WebhookEvent.status == "pending"
                    ).limit(10).all()
                    
                    # Process events concurrently
                    tasks = [self.process_event(event.id) for event in pending_events]
                    if tasks:
                        await asyncio.gather(*tasks, return_exceptions=True)
                
                finally:
                    db.close()
                
                # Wait before next poll
                await asyncio.sleep(settings.WORKER_POLL_INTERVAL)
            
            except Exception as e:
                print(f"Worker error: {e}")
                await asyncio.sleep(settings.WORKER_POLL_INTERVAL)
    
    def stop(self):
        """Stop the worker"""
        self.running = False

# Global worker instance
worker = EventWorker()

