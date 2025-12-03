import requests
import json
import traceback
import time
import hmac
import hashlib

BASE_URL = "http://127.0.0.1:8000"
WEBHOOK_URL = f"{BASE_URL}/webhook"
SECRET = "your-secret-key-change-this"
TENANT_ID = "test-tenant-123"

def generate_signature(body: str, secret: str) -> str:
    signature = hmac.new(
        secret.encode('utf-8'),
        body.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"

def test():
    print(f"Testing {WEBHOOK_URL}")
    payload = {
        "type": "payment.completed",
        "data": {
            "payment_id": "pay_test_123",
            "amount": 1000,
        }
    }
    body = json.dumps(payload)
    signature = generate_signature(body, SECRET)
    headers = {
        "Content-Type": "application/json",
        "X-Signature": signature,
        "X-Tenant-ID": TENANT_ID
    }
    
    try:
        response = requests.post(WEBHOOK_URL, data=body, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    test()
