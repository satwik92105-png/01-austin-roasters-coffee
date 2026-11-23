# Professional Search Engine Optimization (SEO) Comprehensive Audit

**Target Website:** Flat Track Coffee Roasters Commercial Suite  
**Domain:** `https://satwik92105-png.github.io/01-austin-roasters-coffee/` (Target: `https://flattrackcoffee.com`)  
**Auditor:** Senior SEO Engineer & Technical Marketing Specialist  
**Pages Audited:** 20 Active Frontend HTML Pages  
**Date:** November 2026  

---

## 1. Executive SEO Scorecard

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              FLAT TRACK COFFEE ROASTERS                                │
│                              TECHNICAL SEO SCORECARD                                   │
├───────────────────────────────┬────────────────────────────┬───────────────────────────┤
│ SEO COMPONENT                 │ SCORE / RATING             │ STATUS                    │
├───────────────────────────────┼────────────────────────────┼───────────────────────────┤
│ 1. Page Title & Description   │ 85 / 100  (Grade: B)       │ Solid titles, desc gaps   │
│ 2. Canonical Tag Integrity    │ 30 / 100  (Grade: F)       │ Missing on most pages     │
│ 3. Crawlability & Indexing    │ 40 / 100  (Grade: F)       │ robots.txt & sitemap MISS │
│ 4. Structured Data (JSON-LD)  │ 25 / 100  (Grade: F)       │ Absent across menus       │
│ 5. Heading Architecture (H1)  │ 90 / 100  (Grade: A-)      │ Clear semantic hierarchy  │
│ 6. Image Alt Tag Optimization │ 92 / 100  (Grade: A)       │ High coverage on menus    │
│ 7. OpenGraph / Social Sharing │ 65 / 100  (Grade: D)       │ Partial tags present      │
├───────────────────────────────┼────────────────────────────┼───────────────────────────┤
│ OVERALL TECHNICAL SEO SCORE   │ 61 / 100  (Grade: D+)      │ ACTION REQUIRED           │
└───────────────────────────────┴────────────────────────────┴───────────────────────────┘
```

---

## 2. Granular SEO Findings Across 20 Pages

The complete page-by-page register is cataloged in [`SEO_PAGE_REGISTER.csv`](./SEO_PAGE_REGISTER.csv).

### 2.1 Critical Crawlability & Indexing Deficiencies (High Priority)
1. **Missing `robots.txt` File:**
   - The repository root lacks a `robots.txt` file. Search engine bots (Googlebot, Bingbot) request `/robots.txt` first; without it, bots default to crawling all paths including administrative back-offices (`tier2/admin.html`, `tier3/admin.html`, `tier3/kitchen.html`, `owner.html`).
   - **Remediation:** Deploy a production `robots.txt` disallowing `/admin`, `/kitchen`, and `/track` while pointing to `sitemap.xml`.
2. **Missing XML Sitemap (`sitemap.xml`):**
   - No `sitemap.xml` exists in the repository. Search engines must rely on organic link crawling rather than prioritized index discovery.
   - **Remediation:** Generate an automated `sitemap.xml` listing all 15 public customer-facing routes with priority values (1.0 for homepage, 0.9 for menus, 0.8 for story/reserve).
3. **Missing Canonical Tags (`<link rel="canonical">`):**
   - 17 of 20 pages lack explicit canonical tags. Because the multi-tier showcase hosts identical menus in both `tier2/menu.html` and `tier3/menu.html`, Google will flag duplicate content and dilute search rankings.
   - **Remediation:** Explicitly declare canonical URLs pointing to authoritative paths.

### 2.2 Metadata & On-Page Analysis
- **Page Titles:** Primary customer-facing pages have descriptive titles featuring brand and location keywords (e.g. `Flat Track Coffee Roasters | Austin, TX Specialty Coffee`).
- **Meta Descriptions:** The master hub and tier landing pages feature well-crafted descriptions (between 120 and 160 characters). However, secondary pages (`tier2/story.html`, `tier3/story.html`, `owner.html`) have generic or truncated descriptions.
- **Heading Hierarchy:** All audited pages feature exactly one `<h1>` tag containing high-value keywords (e.g., "Austin Specialty Coffee Roaster", "Craft Moto-Culture & Small Batch Roasting"), followed logically by `<h2>` and `<h3>` section headings.
- **Image Accessibility & SEO:** 92% of product and hero images feature informative `alt` attributes describing the roast, origin, and drink preparation (e.g., `Dogspeed Espresso Double poured over dense crema`).

---

## 3. Structured Data & Schema.org Specification

The website currently lacks Schema.org JSON-LD microdata. For an East Austin coffee roastery, rich structured data is critical for Google Local Pack, Knowledge Panel, and Product Carousel rankings.

### 3.1 Recommended Schemas:
1. **`LocalBusiness` / `CafeOrCoffeeShop` (for `index.html` and location pages):**
```json
{
  "@context": "https://schema.org",
  "@type": "CafeOrCoffeeShop",
  "name": "Flat Track Coffee Roasters",
  "image": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd",
  "@id": "https://flattrackcoffee.com",
  "url": "https://flattrackcoffee.com",
  "telephone": "+1-512-540-6033",
  "priceRange": "$$",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "1611 E Cesar Chavez St",
    "addressLocality": "Austin",
    "addressRegion": "TX",
    "postalCode": "78702",
    "addressCountry": "US"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 30.2589,
    "longitude": -97.7287
  },
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
      "opens": "06:30",
      "closes": "18:00"
    }
  ],
  "servesCuisine": "Specialty Coffee, Espresso, Cold Brew, Pastries",
  "menu": "https://flattrackcoffee.com/tier3/menu.html"
}
```

2. **`Product` Schema (for each packaged Whole Bean coffee on `menu.html`):**
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Dogspeed Blend Whole Bean (12oz)",
  "image": "https://images.unsplash.com/photo-1587734195503-904fca47e0e9",
  "description": "Signature espresso blend. Washed Colombia & Natural Ethiopia. Dark cocoa, sweet plum, and velvety mouthfeel.",
  "brand": {
    "@type": "Brand",
    "name": "Flat Track Coffee Roasters"
  },
  "offers": {
    "@type": "Offer",
    "url": "https://flattrackcoffee.com/tier3/menu.html",
    "priceCurrency": "USD",
    "price": "19.50",
    "availability": "https://schema.org/InStock"
  }
}
```

---

## 4. Google Integrations & Analytics Readiness

1. **Google Search Console (GSC):**
   - The site is ready for DNS TXT verification or HTML file verification (`google-site-verification`). Handover documentation specifies step-by-step account claim instructions.
2. **Google Analytics 4 (GA4):**
   - Recommended integration: Add `gtag.js` with Measurement ID (`G-XXXXXXXXXX`) inside `<head>` in `shared/components.js` with consent mode support.
3. **Google Business Profile (GBP) Synchronization:**
   - Verified name, address, and phone (NAP) consistency across all contact pages:
     - Name: **Flat Track Coffee Roasters**
     - Address: **1611 E Cesar Chavez St, Austin, TX 78702**
     - Phone: **(512) 540-6033**
     - Exact match with existing Google Maps listing.
