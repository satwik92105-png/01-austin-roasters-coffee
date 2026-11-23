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

## Phase P0: Immediate Client Demonstration Polish (COMPLETED & VERIFIED)
*Status: COMPLETED (Git Commit: 7d55126) | Verified by: Automated QA Suite*

### P0-1: Correct Unbound Calendar & Email Secondary Anchors on Reservation Confirmation
- **Target Files:** `tier2/reserve.html`, `tier3/reserve.html`
- **Resolution:**
  - Repaired initial fallback `href`s on `#btn-add-calendar`, `#btn-email-self`, `#btn-add-calendar3`, and `#btn-email-self3` with fully valid Google Calendar and RFC 6068 `mailto:` links.
  - Dynamically updates reservation details upon submission (guest name, party size, date/time, reference ID).
  - Verified with `audit/verify_p0_links.py` (4/4 links PASS).
  - Obsolete `backend_server.py` safely removed after confirming zero runtime dependencies.

---

## Phase P1: Critical Pre-Launch Security & Persistence (HARDENING COMPLETED; DB MIGRATION AWAITING APPROVAL)
*Status: SECURITY HARDENING IMPLEMENTED & VERIFIED (16/16 Automated Tests Passing)*

### P1-1: Migrate Ephemeral SQLite to Persistent Cloud PostgreSQL (Neon / Supabase)
- **Target File:** `backend/database.py`
- **Status:** **PENDING CLIENT APPROVAL** (Do not execute without explicit client sign-off).
- **Deliverable:** Authored `audit-results/DATABASE_MIGRATION_PLAN.md` detailing Neon vs Supabase provider comparison, financial projections ($0 to $19/mo), client ownership transfer protocol, zero-downtime ETL migration script, data integrity verification, and instant rollback procedure.

### P1-2: Eliminate Client-Side PII Forwarding to `formsubmit.co`
- **Target Files:** `shared/api-client.js`, `backend/main.py`
- **Status:** **COMPLETED & VERIFIED**.
- **Resolution:**
  - Completely removed unencrypted `formsubmit.co` calls.
  - Implemented secure server-side Resend email proxy (`/api/notifications/send-confirmation`) with schema validation and fallback.

### P1-3: Enforce Comprehensive Admin Authentication & Lockout
- **Target Files:** `backend/auth.py`, `backend/main.py`, `shared/api-client.js`, `tier2/admin.html`, `tier3/admin.html`
- **Status:** **COMPLETED & VERIFIED**.
- **Resolution:**
  - Removed all hardcoded PIN authentication (`1234`, `roastmaster123`, `barista123`) and query parameter `?pin=` bypass mechanisms.
  - Enforced cryptographically signed JWT Bearer tokens for all administrative and kitchen operations.
  - Enforced 5-attempt / 15-minute brute-force lockout across all endpoints.
  - Ephemeral cryptographically random secret enforced when `SECRET_KEY` is not explicitly set in environment (prevents CWE-798 token forgery).

### P1-4: Implement Server-Side Price Verification & Recalculation
- **Target Files:** `backend/main.py`, `backend/schemas.py`
- **Status:** **COMPLETED & VERIFIED**.
- **Resolution:**
  - Server authoritatively looks up database prices and validates stock availability (`in_stock`).
  - Out-of-stock items reject order creation with `400 Bad Request`.
  - Authoritatively parses modifier customizations (e.g. Oat Milk +$0.75, Extra Shot +$1.00) and computes Texas 8.25% sales tax server-side.

### P1-5: Secure Orders & Reservations APIs Against Broken Object-Level Authorization (BOLA)
- **Target File:** `backend/main.py`
- **Status:** **COMPLETED & VERIFIED**.
- **Resolution:**
  - `GET /api/orders`, `GET /api/reservations`, `GET /api/inquiries`, and `GET /api/subscribers` protected with `require_staff` RBAC guard (unauthenticated requests return 401).
  - Customer order tracking endpoint `GET /api/orders/{order_id}` masks customer names (`J***`) and suppresses private phone numbers and financial PII for unauthenticated callers, while providing full data to authenticated staff.

### P1-6: Implement HTTP Security Headers & Restrict CORS
- **Target Files:** `backend/main.py`, `vercel.json`
- **Status:** **COMPLETED & VERIFIED**.
- **Resolution:**
  - Restricted CORS from `allow_origins=["*"]` to explicitly approved origins (`https://satwik92105-png.github.io`, Vercel production, authorized local development ports).
  - Injected complete OWASP security headers (CSP, HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy).
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
