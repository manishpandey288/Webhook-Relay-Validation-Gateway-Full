"""Verify and display database statistics"""
from db.database import SessionLocal
from models.webhook_models import WebhookEvent, DeadLetterEvent, EventAttempt
from sqlalchemy import func

def verify_db():
    """Display database statistics"""
    db = SessionLocal()
    
    try:
        # Total counts
        total_events = db.query(WebhookEvent).count()
        total_dead_letters = db.query(DeadLetterEvent).count()
        total_attempts = db.query(EventAttempt).count()
        
        # Status breakdown
        delivered = db.query(WebhookEvent).filter(WebhookEvent.status == "delivered").count()
        pending = db.query(WebhookEvent).filter(WebhookEvent.status == "pending").count()
        failed = db.query(WebhookEvent).filter(WebhookEvent.status == "failed").count()
        processing = db.query(WebhookEvent).filter(WebhookEvent.status == "processing").count()
        
        # Tenant breakdown
        tenants = db.query(WebhookEvent.tenant_id).distinct().count()
        
        # Event type breakdown
        event_types = db.query(WebhookEvent.event_type).distinct().count()
        
        print("\n" + "="*60)
        print("DATABASE STATISTICS")
        print("="*60)
        print(f"\n📊 WEBHOOK EVENTS")
        print(f"   Total Events:        {total_events}")
        print(f"   ✓ Delivered:         {delivered}")
        print(f"   ⏳ Pending:           {pending}")
        print(f"   ✗ Failed:            {failed}")
        print(f"   ⚙️  Processing:       {processing}")
        
        print(f"\n👥 MULTI-TENANCY")
        print(f"   Unique Tenants:      {tenants}")
        print(f"   Unique Event Types:  {event_types}")
        
        print(f"\n📬 DEAD LETTER QUEUE")
        print(f"   Total Dead Letters:  {total_dead_letters}")
        
        print(f"\n📋 EVENT ATTEMPTS")
        print(f"   Total Attempts:      {total_attempts}")
        
        # Sample recent events
        print(f"\n📌 RECENT EVENTS (Last 5)")
        print("-" * 60)
        recent = db.query(WebhookEvent).order_by(WebhookEvent.created_at.desc()).limit(5).all()
        for event in recent:
            print(f"   [{event.status.upper()}] {event.event_type} (Tenant: {event.tenant_id})")
        
        print("\n" + "="*60)
        print("✓ Database is ready for testing!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_db()
