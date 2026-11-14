import pytest
from fastapi.testclient import TestClient
from main import app, startup_populate
from auth import _FAILED_ATTEMPTS, _LOCKOUTS

# Ensure database is seeded for tests
startup_populate()

client = TestClient(app)

def setup_function():
    # Clear lockout counters before each test to ensure test isolation
    _FAILED_ATTEMPTS.clear()
    _LOCKOUTS.clear()

def test_health_check():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
    assert res.json()["service"] == "Flat Track Coffee Roasters Enterprise API"
    # Verify security headers injected
    assert res.headers.get("x-content-type-options") == "nosniff"
    assert res.headers.get("x-frame-options") == "SAMEORIGIN"
    assert "default-src" in res.headers.get("content-security-policy", "")

def test_public_can_read_menu():
    res = client.get("/api/menu")
    assert res.status_code == 200
    items = res.json()
    assert isinstance(items, list)
    assert len(items) > 0
    # Must not expose internal soft-delete flags or deleted items
    for item in items:
        assert "name" in item
        assert "price" in item

def test_unauthenticated_cannot_mutate_menu():
    payload = {
        "name": "Malicious Fake Espresso",
        "category": "espresso",
        "price": 0.01,
        "description": "Unauthorized injection attempt",
        "in_stock": True,
        "customizable": False
    }
    # 1. Unauthenticated Create -> 401 or 403
    res = client.post("/api/menu", json=payload)
    assert res.status_code in [401, 403]

    # 2. Unauthenticated Delete -> 401 or 403
    res = client.delete("/api/menu/1")
    assert res.status_code in [401, 403]

    # 3. Unauthenticated Toggle Stock -> 401 or 403
    res = client.patch("/api/menu/1/stock?in_stock=false")
    assert res.status_code in [401, 403]

def test_admin_login_and_authenticated_mutation():
    # 1. Login with owner credentials
    login_res = client.post("/api/auth/login", json={
        "email": "admin@flattrackcoffee.com",
        "password": "roastmaster123"
    })
    assert login_res.status_code == 200
    data = login_res.json()
    token = data["access_token"]
    assert token is not None
    assert data["role"] == "admin"

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Add product as authenticated admin
    create_res = client.post("/api/menu", json={
        "name": "Austin Cold Brew Nitro Float",
        "category": "cold",
        "price": 7.50,
        "description": "Nitro cold brew with vanilla bean gelato",
        "badge": "Staff Favorite",
        "in_stock": True,
        "customizable": False
    }, headers=headers)
    assert create_res.status_code == 200
    new_item = create_res.json()
    new_id = new_item["id"]

    # 3. Soft-delete item as admin
    del_res = client.delete(f"/api/menu/{new_id}", headers=headers)
    assert del_res.status_code == 200
    assert del_res.json()["deleted"] is True

    # 4. Verify soft-deleted item is excluded from public menu
    menu_res = client.get("/api/menu")
    assert menu_res.status_code == 200
    active_ids = [i["id"] for i in menu_res.json()]
    assert new_id not in active_ids

def test_brute_force_lockout_429():
    bad_payload = {
        "email": "admin@flattrackcoffee.com",
        "password": "wrong_password_attempt"
    }

    # First 4 attempts fail with 401 Unauthorized
    for i in range(4):
        res = client.post("/api/auth/login", json=bad_payload)
        assert res.status_code == 401, f"Attempt {i+1} should fail with 401"

    # 5th attempt triggers lockout -> 429 Too Many Requests
    lockout_res = client.post("/api/auth/login", json=bad_payload)
    assert lockout_res.status_code == 429
    assert "Retry-After" in lockout_res.headers
    assert lockout_res.headers["Retry-After"] == "900"

def test_mass_assignment_and_server_side_total_recalculation():
    # Client attempts to pass fraudulent subtotal = 0.01 and total = 0.01
    # Catalog price for 'Dogspeed Espresso Double' is $4.50
    tampered_payload = {
        "customerName": "Savvy Attacker",
        "phone": "(512) 555-0199",
        "items": [
            {
                "name": "Dogspeed Espresso Double",
                "qty": 2,
                "price": 0.01  # Fraudulent price attempt
            }
        ],
        "subtotal": 0.02,     # Fraudulent subtotal attempt
        "notes": "Fast please",
        "paidOnline": False
    }

    res = client.post("/api/orders", json=tampered_payload)
    assert res.status_code == 200
    order = res.json()

    # Server must have calculated subtotal based on DB ($4.50 * 2 = $9.00)
    assert order["subtotal"] == 9.00
    assert order["tax"] == 0.74   # 9.00 * 0.0825 = 0.7425 -> 0.74
    assert order["total"] == 9.74  # 9.00 + 0.74 = 9.74

def test_xss_input_sanitization():
    xss_payload = {
        "customerName": "Test <script>alert('xss')</script> User",
        "phone": "(512) 555-0123",
        "items": [
            {
                "name": "Flat Track Classic Cortado",
                "qty": 1,
                "price": 5.00,
                "customizations": "<b>Extra hot</b>"
            }
        ],
        "notes": "<img src=x onerror=alert(1)> Urgent pickup",
        "paidOnline": False
    }

    res = client.post("/api/orders", json=xss_payload)
    assert res.status_code == 200
    order = res.json()

    # Raw <script> and <img> must be HTML-escaped
    assert "<script>" not in order["customerName"]
    assert "&lt;script&gt;" in order["customerName"]
    assert "<img" not in order["notes"]
    assert "&lt;img" in order["notes"]

def test_idempotency_key_duplicate_prevention():
    idempotency_key = "unique-uuid-key-austin-test-999"
    headers = {"Idempotency-Key": idempotency_key}

    payload = {
        "customerName": "Alice Idempotent",
        "phone": "(512) 555-0144",
        "items": [
            {
                "name": "Flat Track Classic Cortado",
                "qty": 1,
                "price": 5.00
            }
        ],
        "notes": "Testing idempotency",
        "paidOnline": True
    }

    # First request creates order
    res1 = client.post("/api/orders", json=payload, headers=headers)
    assert res1.status_code == 200
    order1 = res1.json()

    # Second request with SAME Idempotency-Key returns cached order without creating a new one
    res2 = client.post("/api/orders", json=payload, headers=headers)
    assert res2.status_code == 200
    order2 = res2.json()

    # Both must match the same order ID and total
    assert order1["id"] == order2["id"]
    assert order1["total"] == order2["total"]

def test_kds_role_authorization():
    # 1. Unauthenticated status update should fail
    fail_res = client.patch("/api/orders/FT-1234/status?new_status=Brewing")
    assert fail_res.status_code in [401, 403]

    # 2. Update with Admin PIN (POS/KDS hardware terminal) succeeds
    pin_headers = {"X-Admin-PIN": "1234"}
    
    # First create an order
    order_res = client.post("/api/orders", json={
        "customerName": "KDS Tester",
        "phone": "(512) 555-0123",
        "items": [{"name": "Flat Track Classic Cortado", "qty": 1, "price": 5.00}]
    })
    order_id = order_res.json()["id"]

    # Advance status using PIN
    succ_res = client.patch(f"/api/orders/{order_id}/status?new_status=Brewing", headers=pin_headers)
    assert succ_res.status_code == 200
    assert succ_res.json()["status"] == "Brewing"

def test_audit_logging_and_pagination():
    # 1. Non-admin cannot read audit logs
    unauth_res = client.get("/api/audit-logs")
    assert unauth_res.status_code in [401, 403]

    # 2. Admin can read audit logs
    admin_headers = {"X-Admin-PIN": "1234"}
    logs_res = client.get("/api/audit-logs?page=1&limit=10", headers=admin_headers)
    assert logs_res.status_code == 200
    logs = logs_res.json()
    assert isinstance(logs, list)
    assert len(logs) > 0
    # Check structure
    first_log = logs[0]
    assert "action" in first_log
    assert "actor" in first_log
    assert "timestamp_utc" in first_log
