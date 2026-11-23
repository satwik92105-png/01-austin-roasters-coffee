# Client Handover & Infrastructure Transfer Runbook

**Client Organization:** Flat Track Coffee Roasters (Austin, TX)  
**Project:** Commercial Web Architecture & Operations Suite  
**Authors:** Senior DevOps Engineer & Technical Documentation Specialist  
**Security Warning:** This document contains operational procedures and configuration templates. **No real production secret values or private cryptographic keys are stored within this runbook.**  
**Date:** November 2026  

---

## 1. Ownership & Asset Transfer Checklist

To transfer full legal, technical, and operational control of the website to the coffee shop owner, complete the following transfer actions:

| Asset / Service | Current Custodian | Target Custodian | Transfer Mechanism | Status |
|---|---|---|---|---|
| **GitHub Source Code** | Developer Org / Personal | Client GitHub Org (`flattrack-coffee`) | Settings $\to$ General $\to$ Transfer Repository | Ready for Transfer |
| **Domain Name (`flattrackcoffee.com`)**| Registrar Account | Client Cloudflare / Namecheap Account | Auth Code (EPP Key) Domain Transfer | Instructions Below |
| **DNS Management** | Developer Cloudflare | Client Cloudflare Organization | Add domain to client account; update NS | Instructions Below |
| **Frontend CDN Hosting** | GitHub Pages / Vercel | Client Cloudflare Pages / Vercel Pro | Connect GitHub repo to client account | Instructions Below |
| **Database Cluster** | Ephemeral / Developer | Client Managed PostgreSQL (Supabase/Neon)| Organization Invite $\to$ Owner Role | Instructions Below |
| **Transactional Email** | Unconfigured / FormSubmit | Client Resend Organization (`resend.com`) | Team Invite $\to$ Owner Role | Instructions Below |
| **Stripe Merchant Account** | Test Mode / Simulated | Client Stripe Account (Bank Linked) | Stripe Connect / Standard Account Link | Instructions Below |
| **Google Search Console** | Developer Account | Client Google Workspace Admin | Verification via DNS TXT Record | Instructions Below |
| **Google Analytics 4** | Developer Property | Client GA4 Account | Admin $\to$ Property Access Management | Instructions Below |

---

## 2. DNS Configuration Specification

Configure the following authoritative DNS records within the client's DNS provider (e.g., Cloudflare):

### 2.1 Web Traffic & CDN Records
```dns
# Root apex domain
A       @               192.0.2.1       (Proxied - Cloudflare Edge)
# Subdomain www
CNAME   www             @               (Proxied - Cloudflare Edge)
# API Gateway Subdomain
CNAME   api             cname.vercel-dns.com. (or workers.dev)
```

### 2.2 Transactional Email Authentication Records (Resend)
```dns
# SPF Record
TXT     @               "v=spf1 include:amazonses.com ~all"

# DKIM Cryptographic Key Records (Provided by Resend Dashboard)
CNAME   resend._domainkey.flattrackcoffee.com    dkim.resend.com.
CNAME   resend2._domainkey.flattrackcoffee.com   dkim2.resend.com.
CNAME   resend3._domainkey.flattrackcoffee.com   dkim3.resend.com.

# DMARC Enforcement Policy
TXT     _dmarc          "v=DMARC1; p=quarantine; pct=100; rua=mailto:dmarc@flattrackcoffee.com"
```

---

## 3. Environment Variable Provisioning

The backend application requires the following environment variables configured in Vercel or Cloudflare Workers. **Never commit `.env` files to git repositories.**

| Variable Name | Environment | Description | Example / Format Template |
|---|---|---|---|
| `ENVIRONMENT` | All | Application runtime mode | `production` or `staging` |
| `DATABASE_URL` | Production | Managed PostgreSQL pooled connection | `postgresql://user:[PASSWORD]@db.supabase.co:5432/postgres?sslmode=require` |
| `SECRET_KEY` | Production | 256-bit cryptographically random JWT key | Generate via `openssl rand -hex 32` |
| `ALLOWED_ORIGINS`| Production | Whitelist of frontend domains for CORS | `https://flattrackcoffee.com,https://www.flattrackcoffee.com` |
| `STRIPE_SECRET_KEY`| Production | Live Stripe secret API key | `sk_live_51...` |
| `STRIPE_WEBHOOK_SECRET`| Production | Secret for webhook signature verification | `whsec_...` |
| `RESEND_API_KEY` | Production | Resend transactional email API key | `re_live_...` |
| `SENDER_EMAIL` | Production | Authoritative outbound email sender | `orders@flattrackcoffee.com` |

---

## 4. Initial Administrator Account Provisioning

To prevent well-known default passwords from existing in production, the initial roastery owner account is provisioned via secure command-line bootstrap:

```bash
# Execute within secure server container (not committed to code)
python -c "
from auth import hash_password
from database import SessionLocal
from models import UserModel

db = SessionLocal()
email = input('Enter Roastery Owner Email: ')
password = input('Enter Secure Password: ')

user = UserModel(email=email, hashed_password=hash_password(password), role='admin')
db.add(user)
db.commit()
print('Initial Administrator Account Created Successfully!')
"
```

---

## 5. Disaster Recovery, Backups & Rollback Procedures

### 5.1 Automated Database Backup & Point-in-Time Recovery
- **Backup Schedule:** Daily automated full snapshots executed at 02:00 CST.
- **WAL Archival:** Write-Ahead Logging (WAL) continuously streamed to secure object storage, enabling recovery to any exact second within the last 7 days.
- **Restoration Test Protocol:**
  1. In Supabase/Neon console, select **Backups** $\to$ **Restore to New Project**.
  2. Input target timestamp.
  3. Verify table counts and data integrity on the restored instance.

### 5.2 Deployment Rollback Protocol
If a bad deployment is promoted to live production:
- **Vercel Instant Rollback:**
  1. Open Vercel Dashboard $\to$ Project $\to$ **Deployments**.
  2. Locate previous known-good deployment (e.g., commit `c4c8792`).
  3. Click **Instant Rollback**. Traffic is reverted at edge nodes in under **10 seconds**.
- **Cloudflare Pages Rollback:**
  1. Open Cloudflare Pages Dashboard $\to$ **Deployments**.
  2. Click **Rollback to this deployment** on the desired version.
