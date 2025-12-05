"""Add test data directly to the main database"""
import json
from datetime import datetime
from db.database import SessionLocal, init_db
from models.webhook_models import WebhookEvent, DeadLetterEvent, EventAttempt
from config import settings

def add_test_data():
    """Initialize DB and add sample test data"""
    init_db()
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing = db.query(WebhookEvent).count()
        if existing > 0:
            print(f"Database already has {existing} webhook events. Skipping insertion.")
            return
        
        print(f"Using DATABASE_URL: {settings.DATABASE_URL[:50]}...")
        
        # Sample webhook events
        events = [
            # Passed events
            WebhookEvent(
                tenant_id="tenant-001",
                event_type="user.created",
                payload={"user_id": "user-123", "email": "test@example.com", "name": "Test User"},
                raw_body=json.dumps({"user_id": "user-123", "email": "test@example.com", "name": "Test User"}),
                signature="test-signature-123",
                status="delivered",
                delivered_at=datetime.utcnow(),
                retry_count=0,
                internal_url="https://webhook-relay-validation-gateway-full-production.up.railway.app/internal/webhook"
            ),
            WebhookEvent(
                tenant_id="tenant-001",
                event_type="user.updated",
                payload={"user_id": "user-124", "email": "updated@example.com", "name": "Updated User"},
                raw_body=json.dumps({"user_id": "user-124", "email": "updated@example.com", "name": "Updated User"}),
                signature="test-signature-124",
                status="delivered",
                delivered_at=datetime.utcnow(),
                retry_count=0,
                internal_url="https://webhook-relay-validation-gateway-full-production.up.railway.app/internal/webhook"
            ),
            WebhookEvent(
                tenant_id="tenant-002",
                event_type="payment.completed",
                payload={"payment_id": "pay-789", "amount": 50.00, "currency": "USD"},
                raw_body=json.dumps({"payment_id": "pay-789", "amount": 50.00, "currency": "USD"}),
                signature="test-signature-789",
                status="delivered",
                delivered_at=datetime.utcnow(),
                retry_count=0,
                internal_url="https://webhook-relay-validation-gateway-full-production.up.railway.app/internal/webhook"
            ),
            WebhookEvent(
                tenant_id="tenant-001",
                event_type="order.completed",
                payload={"order_id": "order-789", "total": 149.99, "items": 5},
                raw_body=json.dumps({"order_id": "order-789", "total": 149.99, "items": 5}),
                signature="test-signature-order-789",
                status="delivered",
                delivered_at=datetime.utcnow(),
                retry_count=1,
                internal_url="https://webhook-relay-validation-gateway-full-production.up.railway.app/internal/webhook"
            ),
            WebhookEvent(
                tenant_id="tenant-002",
                event_type="subscription.activated",
                payload={"subscription_id": "sub-001", "plan": "pro", "status": "active"},
                raw_body=json.dumps({"subscription_id": "sub-001", "plan": "pro", "status": "active"}),
                signature="test-signature-sub-001",
                status="delivered",
                delivered_at=datetime.utcnow(),
                retry_count=0,
                internal_url="https://webhook-relay-validation-gateway-full-production.up.railway.app/internal/webhook"
            ),
            # Pending events
            WebhookEvent(
                tenant_id="tenant-001",
                event_type="order.placed",
                payload={"order_id": "order-456", "total": 99.99, "items": 3},
                raw_body=json.dumps({"order_id": "order-456", "total": 99.99, "items": 3}),
                signature="test-signature-456",
                status="pending",
                retry_count=0,
                internal_url="https://webhook-relay-validation-gateway-full-production.up.railway.app/internal/webhook"
            ),
            WebhookEvent(
                tenant_id="tenant-002",
                event_type="refund.initiated",
                payload={"refund_id": "ref-001", "amount": 25.50, "reason": "customer_request"},
                raw_body=json.dumps({"refund_id": "ref-001", "amount": 25.50, "reason": "customer_request"}),
                signature="test-signature-ref-001",
                status="pending",
                retry_count=0,
                internal_url="https://webhook-relay-validation-gateway-full-production.up.railway.app/internal/webhook"
            ),
            # Failed events
            WebhookEvent(
                tenant_id="tenant-002",
                event_type="invoice.generated",
                payload={"invoice_id": "inv-101", "status": "sent"},
                raw_body=json.dumps({"invoice_id": "inv-101", "status": "sent"}),
                signature="test-signature-101",
                status="failed",
                retry_count=3,
                last_error="Connection timeout after 3 retries",
                internal_url="https://webhook-relay-validation-gateway-full-production.up.railway.app/internal/webhook"
            ),
            WebhookEvent(
                tenant_id="tenant-001",
                event_type="notification.sent",
                payload={"notification_id": "notif-001", "type": "email", "recipient": "user@example.com"},
                raw_body=json.dumps({"notification_id": "notif-001", "type": "email", "recipient": "user@example.com"}),
                signature="test-signature-notif-001",
                status="failed",
                retry_count=5,
                last_error="Webhook endpoint returned 500 Internal Server Error",
                internal_url="https://webhook-relay-validation-gateway-full-production.up.railway.app/internal/webhook"
            ),
            WebhookEvent(
                tenant_id="tenant-002",
                event_type="document.processed",
                payload={"doc_id": "doc-555", "pages": 10, "format": "PDF"},
                raw_body=json.dumps({"doc_id": "doc-555", "pages": 10, "format": "PDF"}),
                signature="test-signature-doc-555",
                status="failed",
                retry_count=8,
                last_error="Max retries exceeded (8)",
                internal_url="https://webhook-relay-validation-gateway-full-production.up.railway.app/internal/webhook"
            ),
            WebhookEvent(
                tenant_id="tenant-001",
                event_type="export.completed",
                payload={"export_id": "exp-001", "file_url": "https://example.com/exports/data.csv"},
                raw_body=json.dumps({"export_id": "exp-001", "file_url": "https://example.com/exports/data.csv"}),
                signature="test-signature-exp-001",
                status="failed",
                retry_count=2,
                last_error="Invalid signature verification",
                internal_url="https://webhook-relay-validation-gateway-full-production.up.railway.app/internal/webhook"
            ),
        ]
        
        db.add_all(events)
        db.commit()
        print(f"✓ Added {len(events)} webhook events")
        
        # Add a dead letter event
        dead_letter = DeadLetterEvent(
            webhook_event_id=8,
            tenant_id="tenant-002",
            event_type="invoice.generated",
            payload={"invoice_id": "inv-101", "status": "sent"},
            raw_body=json.dumps({"invoice_id": "inv-101", "status": "sent"}),
            failure_reason="Max retries exceeded",
            retry_count=3,
            replayed=False
        )
        db.add(dead_letter)
        db.commit()
        print(f"✓ Added dead letter event")
        
        # Add event attempts
        attempts = [
            # Successful attempts
            EventAttempt(
                webhook_event_id=1,
                attempt_number=1,
                status="success",
                response_code=200,
                response_body=json.dumps({"status": "received"}),
                retry_delay=0
            ),
            EventAttempt(
                webhook_event_id=2,
                attempt_number=1,
                status="success",
                response_code=200,
                response_body=json.dumps({"status": "received"}),
                retry_delay=0
            ),
            EventAttempt(
                webhook_event_id=3,
                attempt_number=1,
                status="success",
                response_code=200,
                response_body=json.dumps({"status": "received"}),
                retry_delay=0
            ),
            EventAttempt(
                webhook_event_id=4,
                attempt_number=1,
                status="failed",
                response_code=500,
                response_body=json.dumps({"error": "Internal Server Error"}),
                error_message="Server returned 500",
                retry_delay=1
            ),
            EventAttempt(
                webhook_event_id=4,
                attempt_number=2,
                status="success",
                response_code=200,
                response_body=json.dumps({"status": "received"}),
                retry_delay=1
            ),
            EventAttempt(
                webhook_event_id=5,
                attempt_number=1,
                status="success",
                response_code=200,
                response_body=json.dumps({"status": "received"}),
                retry_delay=0
            ),
            # Failed attempts
            EventAttempt(
                webhook_event_id=8,
                attempt_number=1,
                status="failed",
                response_code=500,
                response_body=json.dumps({"error": "Internal Server Error"}),
                error_message="Connection timeout",
                retry_delay=1
            ),
            EventAttempt(
                webhook_event_id=8,
                attempt_number=2,
                status="failed",
                response_code=503,
                response_body=json.dumps({"error": "Service Unavailable"}),
                error_message="Service temporarily unavailable",
                retry_delay=2
            ),
            EventAttempt(
                webhook_event_id=8,
                attempt_number=3,
                status="failed",
                response_code=504,
                response_body=json.dumps({"error": "Gateway Timeout"}),
                error_message="Gateway timeout",
                retry_delay=4
            ),
            EventAttempt(
                webhook_event_id=9,
                attempt_number=1,
                status="failed",
                response_code=500,
                response_body=json.dumps({"error": "Internal Server Error"}),
                error_message="Server error",
                retry_delay=1
            ),
            EventAttempt(
                webhook_event_id=9,
                attempt_number=2,
                status="failed",
                response_code=500,
                response_body=json.dumps({"error": "Internal Server Error"}),
                error_message="Server error persists",
                retry_delay=2
            ),
            EventAttempt(
                webhook_event_id=10,
                attempt_number=1,
                status="failed",
                response_code=400,
                response_body=json.dumps({"error": "Bad Request"}),
                error_message="Invalid payload format",
                retry_delay=0
            ),
            EventAttempt(
                webhook_event_id=10,
                attempt_number=2,
                status="failed",
                response_code=400,
                response_body=json.dumps({"error": "Bad Request"}),
                error_message="Invalid payload format - retried",
                retry_delay=1
            ),
            EventAttempt(
                webhook_event_id=10,
                attempt_number=3,
                status="failed",
                response_code=400,
                response_body=json.dumps({"error": "Bad Request"}),
                error_message="Invalid payload format - final attempt",
                retry_delay=2
            ),
            EventAttempt(
                webhook_event_id=10,
                attempt_number=4,
                status="failed",
                response_code=400,
                response_body=json.dumps({"error": "Bad Request"}),
                error_message="Invalid payload format - max retries exceeded",
                retry_delay=4
            ),
            EventAttempt(
                webhook_event_id=10,
                attempt_number=5,
                status="failed",
                response_code=400,
                response_body=json.dumps({"error": "Bad Request"}),
                error_message="Invalid payload format - max retries exceeded",
                retry_delay=8
            ),
            EventAttempt(
                webhook_event_id=11,
                attempt_number=1,
                status="failed",
                response_code=401,
                response_body=json.dumps({"error": "Unauthorized"}),
                error_message="Invalid signature",
                retry_delay=0
            ),
            EventAttempt(
                webhook_event_id=11,
                attempt_number=2,
                status="failed",
                response_code=401,
                response_body=json.dumps({"error": "Unauthorized"}),
                error_message="Invalid signature - retried",
                retry_delay=1
            ),
        ]
        
        db.add_all(attempts)
        db.commit()
        print(f"✓ Added {len(attempts)} event attempts")
        
        # Verify data
        total_events = db.query(WebhookEvent).count()
        total_dead_letters = db.query(DeadLetterEvent).count()
        total_attempts = db.query(EventAttempt).count()
        
        print("\n✓ Test data added successfully!")
        print(f"  - Webhook Events: {total_events}")
        print(f"  - Dead Letter Events: {total_dead_letters}")
        print(f"  - Event Attempts: {total_attempts}")
        
    except Exception as e:
        print(f"✗ Error adding test data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_test_data()
