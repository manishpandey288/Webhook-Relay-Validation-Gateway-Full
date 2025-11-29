"""
Simple internal webhook receiver for testing

This simulates the internal service that receives forwarded webhooks.

Run with: python internal_webhook_receiver.py
"""
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI(title="Internal Webhook Receiver")

@app.post("/internal/webhook")
async def receive_internal_webhook(request: Request):
    """Receive forwarded webhook from gateway"""
    payload = await request.json()
    
    # Simulate processing
    print(f"✅ Received webhook: {payload.get('type', 'unknown')}")
    print(f"   Payload: {payload}")
    
    # Simulate success (change to return 500 for testing retries)
    return {
        "status": "success",
        "message": "Webhook received and processed",
        "event_type": payload.get("type")
    }

@app.get("/")
async def root():
    return {
        "message": "Internal Webhook Receiver",
        "endpoint": "/internal/webhook (POST)"
    }

if __name__ == "__main__":
    print("Starting Internal Webhook Receiver on port 8001...")
    print("This simulates your internal service that receives forwarded webhooks.")
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")

