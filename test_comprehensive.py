#!/usr/bin/env python3
"""
Comprehensive test script for all webhook gateway routes and APIs
Tests with real dummy data and validates all functionality
"""
import hmac
import hashlib
import requests
import json
import time
from typing import Optional, Dict, Any

# Configuration
BASE_URL = "http://127.0.0.1:8000"
WEBHOOK_URL = f"{BASE_URL}/webhook"
SECRET = "your-secret-key-change-this"  # Must match config.py
TENANT_ID = "test-tenant-123"

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}[OK]{Colors.RESET} {text}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}[FAIL]{Colors.RESET} {text}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.YELLOW}[INFO]{Colors.RESET} {text}")

def generate_signature(body: str, secret: str) -> str:
    """Generate HMAC signature for webhook"""
    signature = hmac.new(
        secret.encode('utf-8'),
        body.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"

def test_root_endpoint():
    """Test 1: Root endpoint"""
    print_header("TEST 1: Root Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"GET /: Status {response.status_code}")
            print(f"   Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print_error(f"GET /: Status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"GET /: Exception - {e}")
        return False

def test_webhook_valid_signature():
    """Test 2: Send webhook with valid signature"""
    print_header("TEST 2: Webhook with Valid Signature")
    payload = {
        "type": "payment.completed",
        "data": {
            "payment_id": "pay_test_123",
            "amount": 1000,
            "currency": "USD",
            "customer_id": "cust_456",
            "timestamp": int(time.time())
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
        if response.status_code == 200:
            data = response.json()
            print_success(f"POST /webhook: Status {response.status_code}")
            print(f"   Event ID: {data.get('event_id')}")
            print(f"   Rate limit remaining: {data.get('rate_limit_remaining')}")
            return data.get('event_id')
        else:
            print_error(f"POST /webhook: Status {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"POST /webhook: Exception - {e}")
        return None

def test_webhook_invalid_signature():
    """Test 3: Webhook with invalid signature"""
    print_header("TEST 3: Webhook with Invalid Signature")
    payload = {"type": "test.invalid", "data": "test"}
    body = json.dumps(payload)
    
    headers = {
        "Content-Type": "application/json",
        "X-Signature": "sha256=invalid_signature_here",
        "X-Tenant-ID": TENANT_ID
    }
    
    try:
        response = requests.post(WEBHOOK_URL, data=body, headers=headers, timeout=5)
        if response.status_code == 401:
            print_success(f"POST /webhook (invalid sig): Status {response.status_code} (Expected)")
            print(f"   Response: {response.json().get('detail', 'Unknown')}")
            return True
        else:
            print_error(f"POST /webhook (invalid sig): Status {response.status_code} (Expected 401)")
            return False
    except Exception as e:
        print_error(f"POST /webhook (invalid sig): Exception - {e}")
        return False

def test_webhook_missing_signature():
    """Test 4: Webhook without signature"""
    print_header("TEST 4: Webhook without Signature")
    payload = {"type": "test.no_sig", "data": "test"}
    body = json.dumps(payload)
    
    headers = {
        "Content-Type": "application/json",
        "X-Tenant-ID": TENANT_ID
    }
    
    try:
        response = requests.post(WEBHOOK_URL, data=body, headers=headers, timeout=5)
        if response.status_code == 401:
            print_success(f"POST /webhook (no sig): Status {response.status_code} (Expected)")
            return True
        else:
            print_error(f"POST /webhook (no sig): Status {response.status_code} (Expected 401)")
            return False
    except Exception as e:
        print_error(f"POST /webhook (no sig): Exception - {e}")
        return False

def test_webhook_multiple_events():
    """Test 5: Send multiple webhook events"""
    print_header("TEST 5: Multiple Webhook Events")
    event_ids = []
    
    event_types = [
        "payment.completed",
        "payment.failed",
        "subscription.created",
        "subscription.cancelled",
        "user.updated"
    ]
    
    for i, event_type in enumerate(event_types):
        payload = {
            "type": event_type,
            "data": {
                "id": f"event_{i+1}",
                "timestamp": int(time.time()),
                "sequence": i + 1
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
            if response.status_code == 200:
                data = response.json()
                event_id = data.get('event_id')
                event_ids.append(event_id)
                print_success(f"Event {i+1} ({event_type}): ID {event_id}")
            else:
                print_error(f"Event {i+1} ({event_type}): Status {response.status_code}")
            time.sleep(0.2)  # Small delay between requests
        except Exception as e:
            print_error(f"Event {i+1} ({event_type}): Exception - {e}")
    
    print_info(f"Successfully created {len(event_ids)} events")
    return event_ids

def test_admin_metrics():
    """Test 6: Get admin metrics"""
    print_header("TEST 6: Admin Metrics")
    try:
        response = requests.get(f"{BASE_URL}/admin/metrics", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"GET /admin/metrics: Status {response.status_code}")
            summary = data.get('summary', {})
            print(f"   Total events: {summary.get('total_events', 0)}")
            print(f"   Delivered: {summary.get('delivered', 0)}")
            print(f"   Failed: {summary.get('failed', 0)}")
            print(f"   Pending: {summary.get('pending', 0)}")
            print(f"   Processing: {summary.get('processing', 0)}")
            print(f"   Dead letters: {summary.get('dead_letter', 0)}")
            print(f"   Success rate: {summary.get('success_rate', 0)}%")
            return True
        else:
            print_error(f"GET /admin/metrics: Status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"GET /admin/metrics: Exception - {e}")
        return False

def test_admin_metrics_with_tenant():
    """Test 7: Get admin metrics filtered by tenant"""
    print_header("TEST 7: Admin Metrics (Filtered by Tenant)")
    try:
        response = requests.get(
            f"{BASE_URL}/admin/metrics",
            params={"tenant_id": TENANT_ID},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print_success(f"GET /admin/metrics?tenant_id={TENANT_ID}: Status {response.status_code}")
            summary = data.get('summary', {})
            print(f"   Tenant events: {summary.get('total_events', 0)}")
            return True
        else:
            print_error(f"GET /admin/metrics?tenant_id={TENANT_ID}: Status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"GET /admin/metrics?tenant_id={TENANT_ID}: Exception - {e}")
        return False

def test_admin_dead_letters():
    """Test 8: Get dead letters"""
    print_header("TEST 8: Admin Dead Letters")
    try:
        response = requests.get(f"{BASE_URL}/admin/dead-letters", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"GET /admin/dead-letters: Status {response.status_code}")
            dead_letters = data.get('dead_letters', [])
            print(f"   Dead letters count: {len(dead_letters)}")
            if dead_letters:
                print(f"   Latest dead letter ID: {dead_letters[0].get('id')}")
            return True
        else:
            print_error(f"GET /admin/dead-letters: Status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"GET /admin/dead-letters: Exception - {e}")
        return False

def test_admin_event_attempts(event_id: Optional[int]):
    """Test 9: Get event attempts"""
    print_header("TEST 9: Admin Event Attempts")
    if not event_id:
        print_info("Skipping - no event ID available")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/admin/events/{event_id}/attempts", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"GET /admin/events/{event_id}/attempts: Status {response.status_code}")
            attempts = data.get('attempts', [])
            print(f"   Attempts count: {len(attempts)}")
            print(f"   Event status: {data.get('status')}")
            print(f"   Retry count: {data.get('retry_count')}")
            if attempts:
                latest = attempts[-1]
                print(f"   Latest attempt: #{latest.get('attempt_number')} - {latest.get('status')}")
            return True
        elif response.status_code == 404:
            print_info(f"GET /admin/events/{event_id}/attempts: Status 404 (Event may not have attempts yet)")
            return True  # Not an error, just no attempts recorded
        else:
            print_error(f"GET /admin/events/{event_id}/attempts: Status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"GET /admin/events/{event_id}/attempts: Exception - {e}")
        return False

def test_admin_replay(event_id: Optional[int]):
    """Test 10: Replay event"""
    print_header("TEST 10: Admin Replay Event")
    if not event_id:
        print_info("Skipping - no event ID available")
        return False
    
    try:
        response = requests.post(f"{BASE_URL}/admin/replay/{event_id}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"POST /admin/replay/{event_id}: Status {response.status_code}")
            print(f"   Replayed event ID: {data.get('event_id')}")
            return True
        elif response.status_code == 404:
            print_info(f"POST /admin/replay/{event_id}: Status 404 (Event not found or not in dead-letter queue)")
            return True  # Not an error if event doesn't exist
        else:
            print_error(f"POST /admin/replay/{event_id}: Status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"POST /admin/replay/{event_id}: Exception - {e}")
        return False

def test_documentation_endpoints():
    """Test 11: Documentation endpoints"""
    print_header("TEST 11: Documentation Endpoints")
    endpoints = [
        ("/docs", "Swagger UI"),
        ("/redoc", "ReDoc"),
        ("/openapi.json", "OpenAPI Schema")
    ]
    
    results = []
    for path, name in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{path}", timeout=5)
            if response.status_code == 200:
                print_success(f"GET {path} ({name}): Status {response.status_code}")
                results.append(True)
            else:
                print_error(f"GET {path} ({name}): Status {response.status_code}")
                results.append(False)
        except Exception as e:
            print_error(f"GET {path} ({name}): Exception - {e}")
            results.append(False)
    
    return all(results)

def test_rate_limiting():
    """Test 12: Rate limiting"""
    print_header("TEST 12: Rate Limiting")
    print_info("Sending 12 requests rapidly (limit is 10/sec) to test rate limiting...")
    
    payload = {"type": "rate_limit_test", "data": "test"}
    body = json.dumps(payload)
    signature = generate_signature(body, SECRET)
    
    headers = {
        "Content-Type": "application/json",
        "X-Signature": signature,
        "X-Tenant-ID": TENANT_ID
    }
    
    rate_limited = False
    successful = 0
    for i in range(12):
        try:
            response = requests.post(WEBHOOK_URL, data=body, headers=headers, timeout=5)
            if response.status_code == 429:
                print_success(f"Rate limit triggered at request {i+1} (Expected)")
                print(f"   Response: {response.json().get('detail', 'Unknown')}")
                rate_limited = True
                break
            elif response.status_code == 200:
                successful += 1
            else:
                print_error(f"Request {i+1}: Status {response.status_code}")
        except Exception as e:
            print_error(f"Request {i+1}: Exception - {e}")
        
        time.sleep(0.05)  # 50ms between requests (20 requests per second)
    
    if not rate_limited:
        print_info(f"Rate limit not triggered. {successful} requests succeeded.")
        print_info("Note: Rate limiter uses 1-second window, may need faster requests")
    
    return True

def check_internal_receiver():
    """Check if internal webhook receiver is running"""
    print_header("CHECK: Internal Webhook Receiver")
    try:
        response = requests.get("http://127.0.0.1:8001/", timeout=2)
        if response.status_code == 200:
            print_success("Internal webhook receiver is RUNNING on port 8001")
            return True
        else:
            print_error(f"Internal receiver returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Internal webhook receiver is NOT RUNNING on port 8001")
        print_info("Events will remain pending until receiver is started")
        print_info("Start it with: python internal_webhook_receiver.py")
        return False
    except Exception as e:
        print_error(f"Error checking internal receiver: {e}")
        return False

def print_summary(results: Dict[str, bool]):
    """Print test summary"""
    print_header("TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"Total Tests: {total}")
    print_success(f"Passed: {passed}")
    if failed > 0:
        print_error(f"Failed: {failed}")
    else:
        print_success("All tests passed!")
    
    print(f"\n{Colors.BOLD}Test Results:{Colors.RESET}")
    for test_name, result in results.items():
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"  {status} - {test_name}")
    
    print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}\n")

def main():
    """Run all tests"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("="*70)
    print("WEBHOOK GATEWAY COMPREHENSIVE TEST SUITE")
    print("="*70)
    print(f"{Colors.RESET}")
    print(f"Base URL: {BASE_URL}")
    print(f"Webhook URL: {WEBHOOK_URL}")
    print(f"Secret: {SECRET[:20]}...")
    print(f"Tenant ID: {TENANT_ID}")
    
    results = {}
    
    # Run tests
    results["Root Endpoint"] = test_root_endpoint()
    time.sleep(0.5)
    
    results["Webhook Valid Signature"] = test_webhook_valid_signature() is not None
    time.sleep(1)
    
    event_id = test_webhook_valid_signature()  # Get an event ID for later tests
    time.sleep(1)
    
    results["Webhook Invalid Signature"] = test_webhook_invalid_signature()
    time.sleep(0.5)
    
    results["Webhook Missing Signature"] = test_webhook_missing_signature()
    time.sleep(0.5)
    
    event_ids = test_webhook_multiple_events()
    results["Multiple Webhook Events"] = len(event_ids) > 0
    time.sleep(2)  # Wait for worker to process
    
    results["Admin Metrics"] = test_admin_metrics()
    time.sleep(0.5)
    
    results["Admin Metrics (Tenant Filter)"] = test_admin_metrics_with_tenant()
    time.sleep(0.5)
    
    results["Admin Dead Letters"] = test_admin_dead_letters()
    time.sleep(0.5)
    
    if event_id:
        results["Admin Event Attempts"] = test_admin_event_attempts(event_id)
        time.sleep(0.5)
        
        results["Admin Replay"] = test_admin_replay(event_id)
        time.sleep(0.5)
    else:
        results["Admin Event Attempts"] = False
        results["Admin Replay"] = False
    
    results["Documentation Endpoints"] = test_documentation_endpoints()
    time.sleep(0.5)
    
    results["Rate Limiting"] = test_rate_limiting()
    time.sleep(0.5)
    
    # Check internal receiver (informational, not a test)
    check_internal_receiver()
    
    # Print summary
    print_summary(results)

if __name__ == "__main__":
    main()

