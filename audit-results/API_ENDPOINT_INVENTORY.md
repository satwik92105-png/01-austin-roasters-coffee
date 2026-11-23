# API Endpoint Inventory & Divergence Audit

**Base URL (Live Production):** `https://01-austin-roasters-coffee.vercel.app/api`  
**Backend Framework:** FastAPI / Python 3.9+  
**Local Codebase Version:** `v22.0` (FastAPI `backend/main.py`)  
**Live Deployed Version:** `v3.1.0` (Demonstrated Version Drift)  
**Total Identified Endpoints:** 15  

---

## Complete Endpoint Matrix

| # | HTTP Method | Endpoint Route | Codebase Intent | Declared Auth | Parameters / Request Body | Live Deployed Response & Status | Security & Architecture Findings |
|---|---|---|---|---|---|---|---|
| **1** | `GET` | `/health` | Service health & version check | Public | None | `200 OK`<br>`{"status": "ok", "version": "3.1.0"}` | **CRITICAL DRIFT:** Live Vercel deployment is running v3.1.0, while local repository is v22.0. |
| **2** | `GET` | `/menu` | Retrieve menu catalog & 86'd status | Public | Optional `?category=...` | `200 OK`<br>Returns JSON list of products | Cache headers absent; client polls periodically. |
| **3** | `GET` | `/orders` | Query active orders | Intended Admin | Optional `?status=...` | `200 OK`<br>Returns order array | **CRITICAL BFLA / DATA EXPOSURE:** Endpoint is unauthenticated in live deployment! Exposes customer names, phones, notes, and full cart contents to anyone. |
| **4** | `POST` | `/orders` | Submit new online order | Public | JSON Order payload (name, phone, items, total) | `201 Created`<br>Returns created order record | **PRICE MANIPULATION RISK:** Backend accepts client-supplied `subtotal`, `tax`, and `total` without server-side recalculation against catalog database. |
| **5** | `GET` | `/orders/{order_id}` | Lookup single order status | Public | Path `order_id` | `200 OK` or `404 Not Found` | Predictable ID enumeration allows harvesting customer contact details. |
| **6** | `PATCH`| `/orders/{order_id}/status`| Update order status (KDS Bump) | Admin/Barista | JSON `{"status": "ready"}` + `?pin=...` | `200 OK` (when PIN provided) | **PIN BYPASS RISK:** Header `X-Admin-PIN` or query `?pin=` accepted directly without brute-force lockout enforcement. |
| **7** | `GET` | `/reservations` | Retrieve booked reservations | Admin | Optional `?date=...` | `200 OK` (live v3.1.0 returns records) | Data exposure of customer reservation names and phone numbers without authentication. |
| **8** | `POST` | `/reservations` | Create table reservation | Public | JSON (name, email, phone, guests, date, time) | `201 Created`<br>Returns booking reference | No CAPTCHA or rate-limiting; susceptible to table booking exhaustion attacks. |
| **9** | `GET` | `/subscriptions` | List active subscriptions | Admin | None | `405 Method Not Allowed` on live v3.1.0 | Live version lacks GET handler; local v22.0 implements full subscription management. |
| **10** | `POST` | `/subscriptions` | Register new coffee subscriber | Public | JSON (plan_id, frequency, grind, customer info) | `201 Created` | Subscription is recorded, but no recurring billing engine (Stripe Billing) is attached. |
| **11** | `POST` | `/catering/quote` | Calculate & record catering inquiry | Public | JSON (guests, service_tier, add_ons, contact) | `200 OK`<br>Returns calculated quote | Quote calculation occurs on client and server, but no rate limiting exists on inquiries. |
| **12** | `POST` | `/auth/login` | Administrative PIN verification | Public / Admin | JSON `{"pin": "1234"}` | `200 OK` or `401 Unauthorized` | 5-attempt brute-force lockout is implemented ONLY in this route, not on direct `?pin=` parameter evaluation! |
| **13** | `POST` | `/checkout/create-session`| Initiate Stripe checkout session | Public | JSON order details | `200 OK`<br>`{"session_id": "cs_test_..."}` | **SIMULATION ONLY:** Returns hardcoded synthetic `cs_test_` string. No real Stripe API calls or webhook verification occur. |
| **14** | `POST` | `/menu/toggle-86` | Toggle 86'd (out-of-stock) item | Admin | JSON `{"item_id": 1, "is_86": true}` | `200 OK` (with PIN) | Modifies in-memory/temporary SQLite record; lost upon Vercel serverless cold restart. |
| **15** | `GET` | `/metrics` | Store analytics & revenue aggregates | Admin | `?pin=...` | `200 OK` (with PIN) | Computes aggregates dynamically from temporary SQLite database. |

---

## Architectural & Infrastructure Divergence Findings

### 1. Ephemeral Storage (`/tmp/flattrack.db`)
In `backend/database.py`:
```python
if os.environ.get("VERCEL"):
    DB_URL = "sqlite:////tmp/flattrack.db"
```
On Vercel Serverless Functions, the filesystem (`/tmp`) is ephemeral and scoped to an individual execution instance. When the container idles or spins down, the entire database is destroyed. Any real orders, table reservations, customer accounts, or 86'd stock changes made by users vanish on the next cold start.

### 2. Third-Party Data Exfiltration Risk (`formsubmit.co`)
In `shared/api-client.js`:
```javascript
// Unauthenticated POST forwarding order payloads to third party
fetch("https://formsubmit.co/ajax/satwik92105@gmail.com", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(orderData)
});
```
Customer names, phone numbers, email addresses, order details, and pickup notes are transmitted in plain JSON to an external third-party form-forwarding service (`formsubmit.co`). This constitutes an unconsented transfer of customer PII under modern privacy frameworks (GDPR / CCPA).
