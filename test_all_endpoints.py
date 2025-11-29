#!/usr/bin/env python3
"""Test all API endpoints"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(method, path, description, **kwargs):
    """Test an endpoint and print results"""
    url = f"{BASE_URL}{path}"
    try:
        if method.upper() == "GET":
            r = requests.get(url, **kwargs)
        elif method.upper() == "POST":
            r = requests.post(url, **kwargs)
        elif method.upper() == "OPTIONS":
            r = requests.options(url, **kwargs)
        else:
            print(f"  ❌ {method} {path}: Unsupported method")
            return
        
        status_icon = "[OK]" if r.status_code < 400 else "[FAIL]"
        print(f"  {status_icon} {method} {path}: Status {r.status_code}")
        
        if r.status_code == 200:
            try:
                data = r.json()
                if isinstance(data, dict) and len(data) > 0:
                    print(f"     Response keys: {list(data.keys())}")
            except:
                pass
        elif r.status_code >= 400:
            try:
                error = r.json()
                print(f"     Error: {error.get('detail', 'Unknown error')[:80]}")
            except:
                print(f"     Error: {r.text[:80]}")
    except Exception as e:
        print(f"  [FAIL] {method} {path}: Exception - {str(e)[:80]}")

print("=" * 60)
print("COMPREHENSIVE API ENDPOINT TEST")
print("=" * 60)
print("\nNOTE: For full testing with webhook delivery, start the")
print("internal webhook receiver: python internal_webhook_receiver.py")
print("=" * 60)

print("\n[ROOT ENDPOINT]")
print("-" * 60)
test_endpoint("GET", "/", "Root endpoint")

print("\n[WEBHOOK ENDPOINTS]")
print("-" * 60)
test_endpoint("OPTIONS", "/webhook", "Webhook options")
test_endpoint("POST", "/webhook", "Webhook (invalid signature - expected 401)", 
              json={"type": "test", "data": "test"},
              headers={"X-Signature": "invalid"})

print("\n[ADMIN ENDPOINTS]")
print("-" * 60)
test_endpoint("GET", "/admin/metrics", "Get metrics")
test_endpoint("GET", "/admin/dead-letters", "Get dead letters")
test_endpoint("GET", "/admin/events/1/attempts", "Get event attempts (may 404 if no event)")
test_endpoint("POST", "/admin/replay/1", "Replay event (may 404 if no event)")

print("\n[DOCUMENTATION ENDPOINTS]")
print("-" * 60)
test_endpoint("GET", "/docs", "Swagger UI")
test_endpoint("GET", "/redoc", "ReDoc")
test_endpoint("GET", "/openapi.json", "OpenAPI schema")

print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)

# Get all registered routes
try:
    r = requests.get(f"{BASE_URL}/openapi.json")
    if r.status_code == 200:
        data = r.json()
        paths = data.get('paths', {})
        print(f"\n[OK] Total registered routes: {len(paths)}")
        print("\nAll registered routes:")
        for path in sorted(paths.keys()):
            methods = list(paths[path].keys())
            print(f"  {' | '.join(m.upper() for m in methods):<15} {path}")
except Exception as e:
    print(f"\n[FAIL] Could not fetch route list: {e}")

print("\n" + "=" * 60)

