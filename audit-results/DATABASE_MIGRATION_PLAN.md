# Flat Track Coffee Roasters — Enterprise Database Migration Plan
**Document Version:** 1.0.0-PROD  
**Status:** DRAFT / PENDING CLIENT APPROVAL (Do NOT execute migration until explicit sign-off)  
**Author:** Senior Database Architect & DevOps Security Team  
**Date:** November 2026  

---

## 1. Executive Summary & Objective

The Flat Track Coffee Roasters backend currently runs on an embedded SQLite database (`backend/flattrack_production.db`). While SQLite has provided ultra-fast zero-latency query execution during local development and MVP prototyping, deploying multi-region serverless execution (e.g., Vercel Functions / AWS Lambda) requires an external, ACID-compliant, concurrently accessible relational database to prevent ephemeral filesystem wipes and data divergence.

This document details the transition strategy to managed **PostgreSQL**.

> [!IMPORTANT]
> In strict compliance with client governance instructions, **this migration is NOT yet executed**. This plan outlines the technical and commercial landscape, operational economics, and risk controls for client approval.

---

## 2. Managed PostgreSQL Provider Comparison

We evaluated four industry-leading managed PostgreSQL platforms based on serverless compatibility, connection pooling, automated point-in-time recovery, Austin Texas compliance, and client ownership ergonomics.

| Provider | Architecture & Serverless Suitability | Connection Pooling | Point-In-Time Recovery (PITR) | Monthly Cost (Starter) | Annual Cost | Client Transfer Ergonomics |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Neon Serverless PostgreSQL** *(Recommended)* | Native scale-to-zero serverless engine with built-in connection pooling for serverless functions (Vercel native integration). | Native built-in PgBouncer over port 6543; HTTP/WebSockets driver available. | 7-day point-in-time restore included on Pro ($19/mo). Free tier has branch history. | **$0.00** (Free Tier)<br>or **$19.00/mo** (Pro) | **$0.00** (Free)<br>or **$228.00/yr** | **Superior:** Direct Vercel marketplace 1-click team ownership transfer. |
| **Supabase (Managed PostgreSQL)** | Dedicated AWS EC2-backed Postgres container with Row-Level Security, Realtime, and built-in Auth. | Supavisor connection pooler built-in on port 6543 (transaction & session mode). | Daily automated backups on Free; 7-day PITR on Pro tier ($25/mo). | **$0.00** (Free Tier)<br>or **$25.00/mo** (Pro) | **$0.00** (Free)<br>or **$300.00/yr** | **Excellent:** Organization member invite and "Transfer Project" button in UI. |
| **Render Managed PostgreSQL** | Traditional managed Postgres instance on AWS infrastructure with persistent NVMe SSD. | External connection pooling required or limited concurrent pool (97 conns). | Automated daily backups; manual point-in-time recovery. | **$7.00/mo** (Basic)<br>or **$20.00/mo** (Standard) | **$84.00/yr**<br>or **$240.00/yr** | **Moderate:** Requires team organization setup and transfer of billing account. |
| **AWS RDS for PostgreSQL** | Traditional enterprise virtual private cloud (VPC) database instance (db.t4g.micro). | Requires configuring AWS RDS Proxy separately ($15+/mo additional). | Automated snapshots up to 35 days with sub-minute PITR. | **$18.00 - $35.00/mo** (Instance + Storage + Egress) | **$216.00 - $420.00/yr** | **Complex:** Requires client to manage full AWS IAM root/organization account. |

### Architectural Recommendation: Neon PostgreSQL
Neon is the optimal choice for Flat Track Coffee Roasters because:
1. **Direct Vercel Serverless Integration:** Serverless functions sleep when idle, incurring zero compute cost during Austin night hours (10:00 PM – 6:00 AM CST).
2. **Built-in PgBouncer:** Solves PostgreSQL connection exhaustion without standing up dedicated proxy servers.
3. **Database Branching:** Allows instant cloning of production schema and sanitized data for staging and QA testing without impacting live operations.

---

## 3. Financial Projections & Operational Economics

### Scenario A: Free Tier Production Validation (Months 1–3)
- **Monthly Compute & Storage:** $0.00 (Neon Free Tier includes 0.5 GiB storage and 100 compute hours/month).
- **SSL/TLS Encryption:** Included free.
- **Estimated Annual Cost:** **$0.00 / year**.

### Scenario B: Commercial Production Growth (Months 4+)
- **Monthly Plan (Neon Pro or Supabase Pro):** $19.00 – $25.00 / month.
- **Compute Sizing:** 0.25 to 1.0 vCPU auto-scaling.
- **Storage:** 10 GB NVMe persistent SSD storage.
- **Backups:** Automated 7-day continuous WAL point-in-time recovery (PITR).
- **Estimated Annual Cost:** **$228.00 – $300.00 / year**.

---

## 4. Client Ownership & Account-Transfer Protocol

To prevent agency vendor lock-in and ensure the Flat Track Coffee Roasters business owner retains 100% legal and operational ownership of their database, the following transfer protocol will be executed:

```mermaid
sequenceDiagram
    participant Agency as Engineering Team
    participant Platform as Neon / Supabase Cloud
    participant Client as Flat Track Owner (client@flattrackcoffee.com)

    Agency->>Platform: 1. Provision Staging & Production Clusters under Project Org
    Agency->>Platform: 2. Complete Schema Migration & Integrity Verification
    Client->>Platform: 3. Create Official Client Organization Account
    Client->>Platform: 4. Add Company Business Credit Card
    Agency->>Platform: 5. Initiate "Transfer Project Ownership" to Client Org
    Platform->>Client: 6. Email Acceptance Prompt sent to Owner
    Client->>Platform: 7. Accept Transfer; Billing transfers to Flat Track Coffee
    Platform->>Agency: 8. Agency permissions demoted to "Developer / Contributor"
```

1. **Owner Account Creation:** Client creates account at `console.neon.tech` using corporate email (`owner@flattrackcoffee.com`).
2. **Billing Assignment:** Client attaches coffee shop operating card; engineering team never handles or stores credit card numbers.
3. **One-Click Handover:** Project ownership transferred via platform organization transfer tool.
4. **Credential Rotation:** Master passwords automatically regenerated upon handover.

---

## 5. Relational Database Architecture

The target PostgreSQL schema preserves all business entities while adopting strict data types, foreign key integrity, and timezone-aware timestamps (`TIMESTAMPTZ`):

```mermaid
erDiagram
    USERS ||--o{ AUDIT_LOGS : performs
    ORDERS ||--o{ ORDER_ITEMS : contains
    USERS {
        int id PK
        string email UK
        string hashed_password
        string role
        timestamptz created_at
    }
    MENU_ITEMS {
        int id PK
        string name
        string category
        numeric price
        text description
        string badge
        boolean in_stock
        string image
        boolean customizable
        boolean is_deleted
        timestamptz deleted_at
    }
    ORDERS {
        varchar id PK
        string customer_name
        varchar phone
        numeric subtotal
        numeric tax
        numeric total
        varchar status
        timestamptz order_time
        text notes
        boolean is_deleted
    }
    RESERVATIONS {
        varchar id PK
        string name
        string email
        string phone
        int party_size
        varchar date
        varchar time
        varchar status
        text notes
        boolean is_deleted
    }
```

---

## 6. Backup & Point-In-Time Restoration Strategy

1. **Continuous WAL Archiving:** Every write-ahead log transaction is streamed to secure AWS S3 buckets in real time.
2. **Point-In-Time Recovery (PITR):** In the event of catastrophic data corruption, the database can be rolled back to any exact second within the last 7 calendar days.
3. **Automated Nightly Snapshot:** Full logical backup generated at 03:00 AM CST via scheduled GitHub Action:
   ```bash
   pg_dump --clean --if-exists --no-owner --no-privileges "$DATABASE_URL" | gzip > "backups/flattrack_backup_$(date +%Y%m%d).sql.gz"
   ```
4. **Disaster Recovery RPO & RTO Targets:**
   - **RPO (Recovery Point Objective):** Under 60 seconds of data loss.
   - **RTO (Recovery Time Objective):** Cluster failover under 5 minutes.

---

## 7. Zero-Downtime Migration Procedure

When approval is granted, the migration will be executed during an off-peak maintenance window (Tuesday 02:00 AM – 03:30 AM CST) following this 8-step protocol:

1. **Pre-Migration Snapshot:** Take immutable filesystem snapshot of `flattrack_production.db` and compute SHA-256 hash.
2. **Read-Only Maintenance Flag:** Activate maintenance banner on frontend checkout (`window.FlatTrackAPI.isMaintenanceMode = true`).
3. **Target Schema Creation:** Apply SQLAlchemy metadata to target PostgreSQL instance:
   ```bash
   python scripts/init_postgres_schema.py --dsn="$TARGET_POSTGRES_URL"
   ```
4. **Data Extraction & Transformation (ETL Pump):** Stream records from SQLite to PostgreSQL with typecasting:
   - Floats cast to `NUMERIC(10, 2)`.
   - UTC string timestamps cast to native `TIMESTAMPTZ`.
   - Boolean integers `1/0` cast to native `BOOLEAN`.
5. **Checksum & Row Count Verification:** Verify 100% parity across `menu_items`, `orders`, `reservations`, `inquiries`, and `users`.
6. **Connection String Swap:** Update `DATABASE_URL` in Vercel environment variables from `sqlite:///flattrack_production.db` to `postgresql://flattrack_user:SECRET@ep-austin.us-east-2.aws.neon.tech/flattrack?sslmode=require`.
7. **Smoke Testing:** Execute automated API verification test suite (`backend/run_tests.py`).
8. **Lift Maintenance Mode:** Restore live ordering and reservations. Total maintenance window duration: **< 12 minutes**.

---

## 8. Rollback Procedure

If any anomaly, data mismatch, or latency spike (> 500ms) occurs during migration verification:

1. **Immediate Abort Signal:** Cease all write operations on PostgreSQL.
2. **Revert Environment Variable:** Update `DATABASE_URL` back to SQLite local URI in Vercel settings.
3. **Instant Redeploy:** Trigger immediate redeploy of previous production commit.
4. **Restore SQLite Backup:** If local file was touched, restore from `backup_pre_hardening/flattrack_production_backup.db`.
5. **Time to Full Recovery:** **< 90 seconds**. Zero customer orders or reservations lost.

---

## 9. Environment Separation (Dev / Staging / Production)

| Environment | Database Target | Connection String Identifier | Access Boundary |
| :--- | :--- | :--- | :--- |
| **Local Development** | SQLite local file | `sqlite:///./flattrack_production.db` | Developer workstation only. Mock fixtures; zero production PII. |
| **CI / Automated Tests**| In-memory SQLite | `sqlite:///:memory:` | Ephemeral GitHub Actions runner; destroyed after each run. |
| **Staging / Preview** | Neon Branch (`ep-staging-branch`) | `postgresql://.../flattrack_staging?sslmode=require` | Isolated preview URLs. Sanitized seed data. |
| **Production** | Neon Primary (`ep-production-main`) | `postgresql://.../flattrack_prod?sslmode=require` | Encrypted Vercel environment secret; restricted IP firewall; full audit logging. |

---

## 10. Approval Sign-Off Checklist

Before migration execution begins, the client and project stakeholders must sign off on:

- [ ] Provider selection confirmed (Neon PostgreSQL recommended).
- [ ] Monthly operational budget approved ($0.00 Free tier or $19.00/mo Pro tier).
- [ ] Maintenance window scheduled (Recommended: Tuesday 02:00 AM CST).
- [ ] Account ownership email address designated by Flat Track management.
- [ ] Formal sign-off received from client to initiate Phase P2.
