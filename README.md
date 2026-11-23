# Flat Track Coffee Roasters — Three-Tier Hospitality Platform & Sales Showcase

**Client Target:** Flat Track Coffee Roasters  
**Location:** 1611 E Cesar Chavez St, Austin, TX 78702  
**Phone:** (512) 540-6033  
**Live GitHub Pages Demo:** [https://satwik92105-png.github.io/01-austin-roasters-coffee/](https://satwik92105-png.github.io/01-austin-roasters-coffee/)

---

## 🌟 Executive Overview & Commercial Architecture

This repository contains the complete, agency-grade digital platform for **Flat Track Coffee Roasters**, engineered to demonstrate a seamless progression across three distinct commercial tiers:

- **Agency Sales Demo Hub (`index.html`):** Package comparison matrix, ROI payback calculator, and 2-minute word-for-word client closing script.
- **Tier 1 ($497 / $500 one-time):** Single-page luxury editorial storefront (`tier1/index.html`). Includes live Austin CST/CDT open/closed indicator, interactive menu showcase tabs (view-only), roastery craft narrative, working Weekend Pass voucher claim, and Google Maps embed for 1611 E Cesar Chavez St.
- **Tier 2 ($997 / $1,500 one-time):** Multi-page operations hub (`tier2/`) with 0% commission mobile pickup ordering, drink customization modal, table reservation engine (future time slots only), exact 2-decimal rounded tax calculation, and an **Isolated Owner Admin POS Portal** (`tier2/admin.html`) with live multi-tab synchronization via `BroadcastChannel`.
- **Tier 3 ($1,997 / $2,000 one-time):** Flagship enterprise suite (`tier3/`) featuring cinematic scroll animations (parallax hero, ambient steam glow, scroll-linked "Seed to Cup" 4-stage interactive timeline, animated counters), recurring bean subscriptions (`tier3/subscribe.html`), B2B espresso cart & wholesale quote calculator (`tier3/catering.html`), live order tracking stepper (`tier3/track.html`), tablet-ready Kitchen Display Screen (`tier3/kitchen.html`), and Owner BI Analytics (`tier3/admin.html`).

---

## 📁 Modular Project Structure

```text
01-austin-roasters-coffee/
├── index.html                   # Agency Sales Demo Hub & 2-Min Pitch Script
├── tier1.html                   # Backward-compatible redirect to tier1/index.html
├── tier2.html                   # Backward-compatible redirect to tier2/index.html
├── tier3.html                   # Backward-compatible redirect to tier3/index.html
├── owner.html                   # Backward-compatible redirect to tier2/admin.html
├── tier1/
│   └── index.html               # Tier 1 Single-Page Editorial Storefront
├── tier2/
│   ├── index.html               # Tier 2 Home & Featured Coffees
│   ├── menu.html                # Tier 2 Order Ahead & Customization Modal
│   ├── reserve.html             # Tier 2 Table Reservation Engine
│   ├── story.html               # Tier 2 Roastery Craft & Heritage
│   ├── contact.html             # Tier 2 Contact & Google Maps Directions
│   └── admin.html               # Tier 2 Isolated Owner Admin POS Terminal
├── tier3/
│   ├── index.html               # Tier 3 Flagship Hero & Scroll Animations
│   ├── menu.html                # Tier 3 Order Ahead & Customizer
│   ├── subscribe.html           # Tier 3 3-Step Bean Subscription Engine
│   ├── catering.html            # Tier 3 B2B Espresso Cart Quote Calculator
│   ├── track.html               # Tier 3 Live Counter Stepper & Rewards
│   ├── reserve.html             # Tier 3 Table Reservation Engine
│   ├── story.html               # Tier 3 Sourcing & Roastery Story
│   ├── contact.html             # Tier 3 Visit & Contact
│   ├── admin.html               # Tier 3 Owner BI & Sales Analytics
│   └── kitchen.html             # Tier 3 Tablet Barista KDS Screen
├── shared/
│   ├── styles.css               # Design System: Deep Roastery tokens & Z-Index scale
│   ├── api-client.js            # Dual-Mode Data Layer (FastAPI + BroadcastChannel fallback)
│   └── components.js            # Demo Controls Pill, Cart Drawer, Toasts, PDF Receipts
└── backend/
    ├── requirements.txt         # FastAPI, Uvicorn, SQLAlchemy, PyJWT
    ├── database.py              # SQLite / PostgreSQL Session configuration
    ├── models.py                # Database entities (Menu, Orders, Bookings, Users)
    ├── schemas.py               # Pydantic validation schemas
    ├── auth.py                  # JWT creation & strict require_admin role check
    ├── main.py                  # REST API endpoints & CORS middleware
    ├── test_security.py         # Automated test suite (enforcing 401/403)
    └── run_tests.py             # Test runner
```

---

## 🔐 Demo Owner Credentials

To access the isolated Owner Management Terminal (`tier2/admin.html`) or Owner BI (`tier3/admin.html`):
- **Email:** `admin@flattrackcoffee.com`
- **Password / PIN:** `roastmaster123` or `1234`
*(Note: These credentials are intentionally kept out of the public customer HTML).*

---

## 🚀 Dual-Mode Architecture & Deployment

### 1. Zero-Fail Static Demo (GitHub Pages)
The client frontend functions autonomously without requiring any external server:
- All CRUD modifications (adding items, changing prices, toggling stock to Sold Out, advancing order tickets) persist in browser storage.
- Multi-tab synchronization is powered by the HTML5 `BroadcastChannel('flat_track_live_sync')` API. If you open `tier2/menu.html` in one tab and `tier2/admin.html` in another, changing an item's status in Admin instantly reflects on the Customer Menu without a page reload.

### 2. Production Python FastAPI Backend (`backend/`)
For full production deployment (e.g. Render, Railway, Fly.io):
```bash
# 1. Navigate to backend directory
cd backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch local API server
python main.py
# Server runs at http://localhost:8000 (API docs at http://localhost:8000/docs)

# 4. Execute automated security tests
python run_tests.py
```

---

## ✅ End-to-End Verification Checklist

| Area | Feature | Status | Notes |
| :--- | :--- | :---: | :--- |
| **Global UI** | Dev Telemetry Tickers | **REMOVED** | Top technical PID/gateway tickers deleted. |
| **Global UI** | Unverified Boasts | **REMOVED** | Removed fake speed & tier claims from cafe headers. |
| **Global UI** | Floating Demo Controls | **ACTIVE** | `✨ Demo Controls` pill with tier switcher & `[Hide]` toggle. |
| **Global UI** | Z-Index Scale | **VERIFIED** | Strict scale (Base 1, Nav 1000, Cart 7000, Drawer 8000, Modal 9000, Toast 9999). |
| **Global UI** | Google Maps | **FIXED** | Real iframe embed for 1611 E Cesar Chavez St + working Get Directions. |
| **Tier 1** | Single-Page Editorial | **VERIFIED** | Live Austin CST badge, menu tabs, Weekend Pass modal, contact form. |
| **Tier 2** | Multi-Page Architecture | **VERIFIED** | True multi-page site (`index`, `menu`, `reserve`, `story`, `contact`). |
| **Tier 2** | Dynamic Menu & Cart | **VERIFIED** | Dynamic rendering, drink customization modal, exact 2-decimal tax. |
| **Tier 2** | Reservations | **VERIFIED** | Future time slots only, saves booking to database/state. |
| **Tier 2** | Isolated Owner Admin | **VERIFIED** | Auth-gated, full CRUD menu manager, 1-click stock toggle, live order queue. |
| **Tier 3** | Bean Rush Mini-Game | **REMOVED** | 100% eliminated from all pages and assets. |
| **Tier 3** | Cinematic Animations | **VERIFIED** | Parallax hero, steam glow, staggered reveals, Seed-to-Cup timeline. |
| **Tier 3** | Subscriptions | **VERIFIED** | 3-step live price calculator (Roast -> Grind -> Frequency). |
| **Tier 3** | B2B Catering Quote | **VERIFIED** | Dynamic event calculator for mobile espresso bars and cold brew kegs. |
| **Tier 3** | Live Order Tracker | **VERIFIED** | Real-time sync with KDS stepper (Paid -> Brewing -> Ready -> Enjoyed). |
| **Tier 3** | Tablet KDS & BI | **VERIFIED** | High-contrast KDS with audio chimes and 1-tap status bumps; BI charts & CSV export. |
| **Backend** | Role Security | **VERIFIED** | 401/403 enforced on all unauthorized write endpoints; 6/6 tests passing. |

---

## 📊 Comprehensive Professional Audit & Production Readiness Deliverables

An exhaustive, evidence-based audit was performed by an independent triple-specialist audit board (Senior QA Automation, Senior Application Security, and Senior Product Consultant).

Every single interactive element (**1,131 total elements**) was individually tested with **zero sampling**, and the complete 160-check security register (**SEC-001 through SEC-160**) was audited against OWASP ASVS 5.0 (Level 2 target).

### 📑 Complete Audit Reports Directory (`audit-results/`)

| Deliverable Report | Relative Link | Summary Scope |
| :--- | :--- | :--- |
| **Executive Summary & Scorecard** | [`EXECUTIVE_SUMMARY.md`](audit-results/EXECUTIVE_SUMMARY.md) | High-level synthesis, metrics & final readiness verdicts |
| **Initial Project Assessment** | [`INITIAL_PROJECT_ASSESSMENT.md`](audit-results/INITIAL_PROJECT_ASSESSMENT.md) | Baseline architecture, tech stack & code-vs-doc comparison |
| **Full Master Technical Report** | [`FULL_AUDIT_REPORT.md`](audit-results/FULL_AUDIT_REPORT.md) | Unified technical document combining all 3 audit roles |
| **Infrastructure Architecture & Costs** | [`INFRASTRUCTURE_ARCHITECTURE.md`](audit-results/INFRASTRUCTURE_ARCHITECTURE.md) | Vercel vs Cloudflare vs Supabase migration & monthly budget |
| **160-Check Security Register** | [`SECURITY_TEST_REGISTER.csv`](audit-results/SECURITY_TEST_REGISTER.csv) | Master OWASP ASVS 5.0 L2 register (SEC-001 to SEC-160) |
| **STRIDE Threat Model** | [`THREAT_MODEL.md`](audit-results/THREAT_MODEL.md) | Trust boundaries, data flows, threat agents & mitigations |
| **Vulnerability Remediation Guide** | [`VULNERABILITY_REMEDIATION.md`](audit-results/VULNERABILITY_REMEDIATION.md) | Drop-in code fixes for all critical and high security findings |
| **Element-by-Element Test Register** | [`ELEMENT_BY_ELEMENT_TEST_REGISTER.csv`](audit-results/ELEMENT_BY_ELEMENT_TEST_REGISTER.csv) | 1,131 individual element records (zero sampling) |
| **Functional QA Results** | [`FUNCTIONAL_TEST_RESULTS.md`](audit-results/FUNCTIONAL_TEST_RESULTS.md) | Product matrix, cart calculation & checkout test results |
| **Page Inventory (20 Pages)** | [`PAGE_INVENTORY.md`](audit-results/PAGE_INVENTORY.md) | Route mapping, layouts & component catalog |
| **API Endpoint Inventory** | [`API_ENDPOINT_INVENTORY.md`](audit-results/API_ENDPOINT_INVENTORY.md) | 24 endpoints, schemas, auth & live version drift audit |
| **Database & Data Integrity** | [`DATABASE_INTEGRITY_REPORT.md`](audit-results/DATABASE_INTEGRITY_REPORT.md) | Models, ACID properties, backups & persistence audit |
| **Resend Email Integration** | [`EMAIL_INTEGRATION_REPORT.md`](audit-results/EMAIL_INTEGRATION_REPORT.md) | Transactional email setup, templates & deliverability |
| **Technical SEO Audit** | [`SEO_REPORT.md`](audit-results/SEO_REPORT.md) | Metadata, sitemap, indexing & canonical directives |
| **Page-by-Page SEO Register** | [`SEO_PAGE_REGISTER.csv`](audit-results/SEO_PAGE_REGISTER.csv) | Titles, meta descriptions, H1s & word counts for 20 pages |
| **Performance & Core Web Vitals** | [`PERFORMANCE_REPORT.md`](audit-results/PERFORMANCE_REPORT.md) | LCP, INP, CLS benchmarks & caching optimizations |
| **Structured Data Validation** | [`STRUCTURED_DATA_VALIDATION.md`](audit-results/STRUCTURED_DATA_VALIDATION.md) | Schema.org JSON-LD definitions for LocalBusiness & Menu |
| **WCAG 2.2 AA Accessibility** | [`ACCESSIBILITY_REPORT.md`](audit-results/ACCESSIBILITY_REPORT.md) | Contrast ratios, focus states, screen reader semantics |
| **Customer Experience UX Report** | [`CUSTOMER_EXPERIENCE_REPORT.md`](audit-results/CUSTOMER_EXPERIENCE_REPORT.md) | E-commerce flow, drink customizer & mobile viewports |
| **Business Owner ROI Report** | [`BUSINESS_OWNER_REPORT.md`](audit-results/BUSINESS_OWNER_REPORT.md) | Austin specialty coffee commercial viability & payback |
| **Remediation Roadmap** | [`REMEDIATION_ROADMAP.md`](audit-results/REMEDIATION_ROADMAP.md) | Prioritized P0–P3 roadmap with effort & acceptance tests |
| **Client Handover & Runbook** | [`CLIENT_HANDOVER_DOCUMENTATION.md`](audit-results/CLIENT_HANDOVER_DOCUMENTATION.md) | Production transfer manual, credentials & recovery guide |
| **Playwright Automated Tests** | [`test-results.json`](audit-results/test-results.json) | Machine-readable Playwright test results & trace artifacts |
| **Master Project Plan PDF (Clickable)**| [`MASTER_PROJECT_PLAN_AND_SECURITY_AUDIT.pdf`](MASTER_PROJECT_PLAN_AND_SECURITY_AUDIT.pdf) | 8-Page Executive PDF with 58 native clickable hyperlinks |

