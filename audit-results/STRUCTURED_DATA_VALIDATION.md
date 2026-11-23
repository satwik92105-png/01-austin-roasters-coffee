# Structured Data & Schema.org Validation Specification

**Standard Reference:** Google Search Central Structured Data Guidelines & Schema.org v24.0  
**Project:** Flat Track Coffee Roasters Commercial Web Architecture  
**Audit Status:** Schema Specification & Validation Complete  
**Date:** November 2026  

---

## 1. Schema Validation Framework & Ethical Boundaries

Per Part 7 of the project directive:
- **No Fabricated Data:** Schema fields must strictly mirror verified real-world facts. Rating values, review counts, prices, and operating hours must never be inflated.
- **Accurate Business Categorization:** Flat Track operates as a specialty coffee roaster, espresso bar, and vintage moto community space in East Austin. Appropriate types: `CafeOrCoffeeShop`, `CoffeeShop`, `LocalBusiness`, and `Product`.

---

## 2. Validated Schema Payloads by Page

### 2.1 Storefront Homepage (`index.html`, `tier1/index.html`, `tier2/index.html`, `tier3/index.html`)
**Schema Type:** `CafeOrCoffeeShop` + `LocalBusiness`  
**Validation Status:** Passed Google Rich Results Test Syntax Standards.

```json
{
  "@context": "https://schema.org",
  "@type": "CafeOrCoffeeShop",
  "name": "Flat Track Coffee Roasters",
  "alternateName": "Flat Track Coffee",
  "url": "https://flattrackcoffee.com",
  "logo": "https://flattrackcoffee.com/assets/logo.png",
  "image": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=1200&auto=format&fit=crop&q=80",
  "description": "Specialty third-wave coffee roaster and cafe in East Austin blending artisan small-batch coffee with vintage motorcycle culture.",
  "telephone": "+1-512-540-6033",
  "priceRange": "$$",
  "currenciesAccepted": "USD",
  "paymentAccepted": "Cash, Credit Card, Apple Pay, Google Pay, Stripe",
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
  "hasMap": "https://maps.google.com/?q=1611+E+Cesar+Chavez+St,+Austin,+TX+78702",
  "sameAs": [
    "https://www.instagram.com/flattrackcoffee/",
    "https://www.facebook.com/flattrackcoffee/"
  ],
  "servesCuisine": [
    "Specialty Coffee",
    "Espresso",
    "Cold Brew",
    "Artisan Pastries"
  ]
}
```

### 2.2 Menu & Direct Ordering (`tier2/menu.html`, `tier3/menu.html`)
**Schema Type:** `Menu` with itemized `MenuItem` entries.  
**Validation Status:** Fully compliant with Google Restaurant Menu Schema.

```json
{
  "@context": "https://schema.org",
  "@type": "Menu",
  "name": "Flat Track Roastery & Cafe Menu",
  "url": "https://flattrackcoffee.com/tier3/menu.html",
  "hasMenuSection": [
    {
      "@type": "MenuSection",
      "name": "Espresso & Handcrafted Drinks",
      "hasMenuItem": [
        {
          "@type": "MenuItem",
          "name": "Dogspeed Espresso Double",
          "description": "Double-pulled Dogspeed blend. Rich dark cacao, candied citrus, dense persistent crema. The house signature.",
          "offers": {
            "@type": "Offer",
            "price": "4.50",
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock"
          }
        },
        {
          "@type": "MenuItem",
          "name": "Flat Track Classic Cortado",
          "description": "Equal parts double espresso and silky steamed oat or whole milk. Balanced, intensely aromatic.",
          "offers": {
            "@type": "Offer",
            "price": "5.00",
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock"
          }
        },
        {
          "@type": "MenuItem",
          "name": "Bourbon Smoked Vanilla Latte",
          "description": "House-made Madagascar vanilla syrup infused with oak barrel smoke and espresso, topped with raw turbinado sugar.",
          "offers": {
            "@type": "Offer",
            "price": "6.75",
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock"
          }
        }
      ]
    },
    {
      "@type": "MenuSection",
      "name": "Fresh Whole Bean Coffees (12oz)",
      "hasMenuItem": [
        {
          "@type": "MenuItem",
          "name": "Dogspeed Blend Whole Bean (12oz)",
          "description": "Signature espresso blend (Washed Colombia & Natural Ethiopia). Dark cocoa, sweet plum, and velvety mouthfeel.",
          "offers": {
            "@type": "Offer",
            "price": "19.50",
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock"
          }
        },
        {
          "@type": "MenuItem",
          "name": "Mexico Oaxaca Pluma Whole Bean (12oz)",
          "description": "Washed process micro-lot from Pluma Hidalgo. Milk chocolate, crisp green apple, and raw sugar cane sweetness.",
          "offers": {
            "@type": "Offer",
            "price": "21.00",
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock"
          }
        }
      ]
    }
  ]
}
```

### 2.3 Breadcrumb Navigation Schema (`BreadcrumbList`)
For nested pages (`tier2/menu.html`, `tier3/reserve.html`, `tier3/catering.html`):

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://flattrackcoffee.com/"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Roastery Menu",
      "item": "https://flattrackcoffee.com/tier3/menu.html"
    }
  ]
}
```

---

## 3. Implementation Injection Strategy

To ensure zero maintenance overhead, inject structured data programmatically via `shared/components.js` during initial DOM load, matching the current page route and dynamically reflecting active menu pricing.
