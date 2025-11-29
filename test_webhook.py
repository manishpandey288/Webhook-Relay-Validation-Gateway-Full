"""
Test script for webhook system

Usage:
    python test_webhook.py
"""
import hmac
import hashlib
import requests
import json
import time

# Configuration
WEBHOOK_URL = "http://localhost:8000/webhook"
SECRET = "your-secret-key-change-this"  # Should match config.py
TENANT_ID = "test-tenant-123"

def generate_signature(body: str, secret: str) -> str:
    """Generate HMAC signature"""
    signature = hmac.new(
        secret.encode('utf-8'),
        body.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"

def send_webhook(payload: dict, tenant_id: str = None):
    """Send a test webhook"""
    body = json.dumps(payload)
    signature = generate_signature(body, SECRET)
    
    headers = {
        "Content-Type": "application/json",
        "X-Signature": signature
    }
    
    if tenant_id:
        headers["X-Tenant-ID"] = tenant_id
    
    try:
        response = requests.post(WEBHOOK_URL, data=body, headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_basic_webhook():
    """Test 1: Basic webhook"""
    print("\n=== Test 1: Basic Webhook ===")
    payload = {
        "type": "payment.completed",
        "data": {
            "payment_id": "pay_123",
            "amount": 1000,
            "currency": "USD"
        }
    }
    send_webhook(payload, TENANT_ID)

def test_invalid_signature():
    """Test 2: Invalid signature"""
    print("\n=== Test 2: Invalid Signature ===")
    payload = {"type": "test", "data": "test"}
    body = json.dumps(payload)
    
    headers = {
        "Content-Type": "application/json",
        "X-Signature": "sha256=invalid_signature",
        "X-Tenant-ID": TENANT_ID
    }
    
    try:
        response = requests.post(WEBHOOK_URL, data=body, headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_rate_limiting():
    """Test 3: Rate limiting"""
    print("\n=== Test 3: Rate Limiting (sending 15 events quickly) ===")
    payload = {"type": "rate_limit_test", "data": "test"}
    
    for i in range(15):
        print(f"Sending event {i+1}...")
        response = send_webhook(payload, TENANT_ID)
        if response and response.status_code == 429:
            print(f"Rate limit hit at event {i+1}")
            break
        time.sleep(0.1)

def test_metrics():
    """Test 4: Get metrics"""
    print("\n=== Test 4: Get Metrics ===")
    try:
        response = requests.get("http://localhost:8000/admin/metrics", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Metrics: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_dead_letters():
    """Test 5: Get dead letters"""
    print("\n=== Test 5: Get Dead Letters ===")
    try:
        response = requests.get("http://localhost:8000/admin/dead-letters", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Dead Letters: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Webhook Gateway Test Script")
    print("=" * 50)
    print(f"Webhook URL: {WEBHOOK_URL}")
    print(f"Secret: {SECRET}")
    print(f"Tenant ID: {TENANT_ID}")
    print("=" * 50)
    
    # Run tests
    test_basic_webhook()
    time.sleep(1)
    
    test_invalid_signature()
    time.sleep(1)
    
    test_rate_limiting()
    time.sleep(1)
    
    test_metrics()
    time.sleep(1)
    
    test_dead_letters()
    
    print("\n=== Tests Complete ===")

