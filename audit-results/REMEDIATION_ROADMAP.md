# Technical Remediation Roadmap & Implementation Guide

**Target Application:** Flat Track Coffee Roasters Platform  
**Purpose:** Actionable, prioritized engineering plan to transition the platform from client demonstration excellence to full, secure production operations.  

---

## Remediation Priority Matrix

```
  URGENCY / IMPACT
      ▲
   P0 │  [P0-1: Empty Hash Links on Calendar/Email]
      │
   P1 │  [P1-1: Persistent Database]   [P1-2: Remove formsubmit.co PII Exfiltration]
      │  [P1-3: Admin PIN Lockout]     [P1-4: Server-Side Price Verification]
      │  [P1-5: Restrict /orders API]  [P1-6: Security Headers in vercel.json]
      │
   P2 │  [P2-1: Real Stripe Webhooks]  [P2-2: ESC/POS Thermal Receipt Printing]
      │  [P2-3: SendGrid Transactional Emails]
      │
   P3 │  [P3-1: Multi-Location Inventory] [P3-2: Twilio SMS Alerts]
      └────────────────────────────────────────────────────────────────────────►
                                COMPLEXITY & EFFORT
```

---

## Phase P0: Immediate Client Demonstration Polish (Zero Backend Risk)
*Target Completion: < 1 Day | Priority: IMMEDIATE*

### P0-1: Correct Unbound Calendar & Email Secondary Anchors on Reservation Confirmation
- **Target Files:** `tier2/reserve.html`, `tier3/reserve.html`
- **Current Behavior:** `btn-add-calendar` and `btn-email-self` have `href="#"` and lack active JavaScript event listeners, causing a page jump when clicked.
- **Remediation:**
  Attach dynamic event handlers that generate a standard Google Calendar event URL (`https://calendar.google.com/calendar/render?action=TEMPLATE&text=Flat+Track+Coffee+Reservation...`) and a pre-formatted `mailto:` URI with reservation details.
- **Acceptance Criteria:**
  Clicking "Add to Google Calendar" opens a new tab with Google Calendar pre-filled with date, time, and party size.

---

## Phase P1: Critical Pre-Launch Security & Persistence (MANDATORY Before Live Launch)
*Target Completion: 1–2 Weeks | Priority: HIGHEST (BLOCKER FOR REAL MONEY TRANSACTIONS)*

### P1-1: Migrate Ephemeral SQLite to Persistent Cloud PostgreSQL (Neon / Supabase)
- **Target File:** `backend/database.py`
- **Issue:** SQLite database hosted on `/tmp/flattrack.db` is destroyed upon Vercel serverless cold starts.
- **Remediation:**
  1. Provision a free-tier or production Postgres instance on Neon (`postgresql://...`).
  2. Set `DATABASE_URL` in Vercel environment variables.
  3. Replace SQLite connection string with async SQLAlchemy/PostgreSQL engine with connection pooling (`pool_size=5`, `max_overflow=10`).
- **Acceptance Criteria:**
  Orders and reservations placed survive across cold restarts and multi-region Vercel invocations.

### P1-2: Eliminate Client-Side PII Forwarding to `formsubmit.co`
- **Target File:** `shared/api-client.js`
- **Issue:** Cleartext customer names, phone numbers, and order items are posted to an unauthenticated external endpoint.
- **Remediation:**
  Remove lines 928–945 from `shared/api-client.js`. Move email notifications entirely to server-side background tasks triggered after order creation.
- **Acceptance Criteria:**
  Zero network calls to `formsubmit.co` observed in browser DevTools during checkout.

### P1-3: Enforce Comprehensive Admin Authentication & Lockout
- **Target Files:** `backend/auth.py`, `backend/main.py`
- **Issue:** Query parameter PINs (`?pin=1234`) bypass failed-attempt lockouts on protected endpoints.
- **Remediation:**
  1. Remove query-parameter PIN extraction from all API routes.
  2. Require JWT Bearer tokens issued exclusively by `/api/auth/login`.
  3. Hash PINs using `bcrypt` or Argon2id instead of storing them in plaintext strings.
  4. Enforce Redis/in-memory rate limiting (max 5 attempts per IP per 15 minutes).
- **Acceptance Criteria:**
  Sending invalid PINs 5 times blocks the client IP across ALL endpoints; protected routes return `401 Unauthorized` without a valid JWT.

### P1-4: Implement Server-Side Price Verification & Recalculation
- **Target Files:** `backend/main.py`, `backend/schemas.py`
- **Issue:** The server accepts client-supplied `subtotal`, `tax`, and `total` without validation.
- **Remediation:**
  In `POST /api/orders`, look up item prices in the database, calculate modifier costs, apply Texas 8.25% sales tax, and compute the official subtotal and total on the server. Reject the request if client-provided total diverges by more than $0.01.
- **Acceptance Criteria:**
  Sending tampered `total: 0.01` with $20.00 worth of coffee items returns HTTP `400 Bad Request: Price mismatch`.

### P1-5: Secure Orders API Against Broken Object-Level Authorization (BOLA)
- **Target File:** `backend/main.py`
- **Issue:** `GET /api/orders` is public and returns all customer PII.
- **Remediation:**
  1. Protect `GET /api/orders` with admin/barista role authentication.
  2. Protect `GET /api/orders/{order_id}` by requiring a cryptographically secure 128-bit tracking token (`order_token`) returned only to the customer at checkout.
- **Acceptance Criteria:**
  Unauthenticated GET to `/api/orders` returns `401 Unauthorized`.

### P1-6: Implement HTTP Security Headers & Restrict CORS
- **Target File:** `vercel.json`
- **Remediation:**
  Configure strict headers:
```json
"headers": [
  {
    "source": "/(.*)",
    "headers": [
      { "key": "X-Frame-Options", "value": "DENY" },
      { "key": "X-Content-Type-Options", "value": "nosniff" },
      { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
      { "key": "Strict-Transport-Security", "value": "max-age=31536000; includeSubDomains" }
    ]
  }
]
```

---

## Phase P2: Commercial Operations & Payment Verification
*Target Completion: 2–3 Weeks | Priority: HIGH*

### P2-1: Production Stripe Integration with Webhook Signatures
- Integrate official `stripe-python` SDK.
- Use Stripe Checkout or Payment Element with server-side client secrets.
- Verify incoming webhooks via `stripe.Webhook.construct_event` and `STRIPE_WEBHOOK_SECRET`.
- Only mark orders as `paid` upon receiving `checkout.session.completed`.

### P2-2: ESC/POS Thermal Receipt Printing for In-Store Baristas
- Provide automated order ticket dispatch to local counter printers (e.g., Epson TM-T88VI or Star Micronics TSP143) via web print daemon or local network socket.

### P2-3: Transactional Email Infrastructure (Postmark / SendGrid)
- Dispatch branded HTML receipts and pickup notifications with DKIM/SPF verification.

---

## Phase P3: Enterprise Scale & Growth
*Target Completion: Post-Launch | Priority: MEDIUM*

- **P3-1:** Multi-location inventory synchronization between East Cesar Chavez and mobile event pop-ups.
- **P3-2:** Automated SMS pickup notifications via Twilio ("Your flat white is ready at the pickup window!").
- **P3-3:** Customer loyalty reward accounts with QR code scanning at the counter.
