from fastapi import APIRouter, Request, HTTPException, Header, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import json

from db.database import get_db
from controllers.hmac_verifier import verify_hmac_signature
from controllers.rate_limiter import RateLimiter
from models.webhook_models import WebhookEvent
from config import settings

router = APIRouter()
rate_limiter = RateLimiter()

@router.post("/webhook")
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_signature: Optional[str] = Header(None, alias="X-Signature"),
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
    db: Session = Depends(get_db)
):
    """
    STEP 1 & 2: Receive webhook and verify HMAC signature
    """
    # Get raw body
    body = await request.body()
    body_str = body.decode('utf-8')
    
    # STEP 2: Verify HMAC signature
    if not verify_hmac_signature(body, x_signature, settings.WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # STEP 9: Rate limiting
    tenant_id = x_tenant_id or "default"
    is_allowed, remaining = rate_limiter.check_rate_limit(tenant_id)
    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Limit: {settings.DEFAULT_RATE_LIMIT}/sec"
        )
    
    # Parse payload
    try:
        payload = json.loads(body_str)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    event_type = payload.get("type", "unknown")
    
    # STEP 3: Save to database
    webhook_event = WebhookEvent(
        tenant_id=tenant_id,
        event_type=event_type,
        payload=payload,
        raw_body=body_str,
        signature=x_signature,
        status="pending",
        internal_url=settings.INTERNAL_WEBHOOK_URL
    )
    db.add(webhook_event)
    db.commit()
    db.refresh(webhook_event)
    
    # STEP 4: Event is saved with status "pending", worker will pick it up
    # No need to explicitly queue - worker polls database
    
    return JSONResponse(
        status_code=200,
        content={
            "status": "received",
            "event_id": webhook_event.id,
            "rate_limit_remaining": remaining
        }
    )

