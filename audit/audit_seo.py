import os, re, csv

pages = [
    ("index.html", "Hub", "Master Agency Sales Hub"),
    ("demo.html", "Sales", "Client Pitch & Amenities Showcase"),
    ("owner.html", "Portal", "Store Manager Gateway"),
    ("tier1/index.html", "Tier 1", "Single-Page Editorial Roastery Showcase"),
    ("tier2/index.html", "Tier 2", "Corporate Multi-Page Homepage"),
    ("tier2/menu.html", "Tier 2", "Direct Ordering & POS Menu"),
    ("tier2/reserve.html", "Tier 2", "Table Reservation Engine"),
    ("tier2/story.html", "Tier 2", "Moto Heritage & Sourcing Story"),
    ("tier2/contact.html", "Tier 2", "Location, Hours & Inquiry Form"),
    ("tier2/admin.html", "Tier 2", "Store Operations POS"),
    ("tier3/index.html", "Tier 3", "Enterprise Digital Roastery Homepage"),
    ("tier3/menu.html", "Tier 3", "Flagship Commercial Menu & Checkout"),
    ("tier3/reserve.html", "Tier 3", "VIP Table & Cupping Reservation"),
    ("tier3/story.html", "Tier 3", "Interactive Cupping & Origin Story"),
    ("tier3/contact.html", "Tier 3", "Department Inquiries & Location"),
    ("tier3/subscribe.html", "Tier 3", "Coffee Club Subscription Configurator"),
    ("tier3/catering.html", "Tier 3", "Event Catering Instant Quote Calculator"),
    ("tier3/track.html", "Tier 3", "Live Customer Order Tracking Stepper"),
    ("tier3/kitchen.html", "Tier 3", "Barista Kitchen Display System (KDS)"),
    ("tier3/admin.html", "Tier 3", "Enterprise Management Back-Office")
]

base_dir = r"C:\Users\HP\.gemini\antigravity\scratch\repo_01_coffee"

seo_rows = []

for rel_path, tier, desc in pages:
    full_path = os.path.join(base_dir, rel_path)
    if not os.path.exists(full_path):
        continue
    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Title
    t_match = re.search(r"<title>(.*?)</title>", content, re.I | re.S)
    title = t_match.group(1).strip() if t_match else ""

    # Meta Description
    d_match = re.search(r"<meta\s+name=[\"']description[\"']\s+content=[\"'](.*?)[\"']", content, re.I | re.S)
    meta_desc = d_match.group(1).strip() if d_match else ""

    # Canonical
    c_match = re.search(r"<link\s+rel=[\"']canonical[\"']\s+href=[\"'](.*?)[\"']", content, re.I | re.S)
    canonical = c_match.group(1).strip() if c_match else ""

    # Open Graph Title
    og_t = re.search(r"<meta\s+property=[\"']og:title[\"']\s+content=[\"'](.*?)[\"']", content, re.I | re.S)
    og_title = og_t.group(1).strip() if og_t else ""

    # Schema JSON-LD
    has_schema = bool(re.search(r"<script\s+type=[\"']application/ld\+json[\"']", content, re.I))

    # H1 count
    h1s = len(re.findall(r"<h1[\s>]", content, re.I))
    # H2 count
    h2s = len(re.findall(r"<h2[\s>]", content, re.I))

    # Image Alt Coverage
    total_imgs = len(re.findall(r"<img[\s>]", content, re.I))
    alt_imgs = len(re.findall(r"<img[^>]+alt=[\"'][^\"']+[\"']", content, re.I))

    # Index Directive
    robots_meta = re.search(r"<meta\s+name=[\"']robots[\"']\s+content=[\"'](.*?)[\"']", content, re.I)
    robots = robots_meta.group(1).strip() if robots_meta else "index, follow"

    # Status Determination
    status = "PASS"
    issues = []
    if not title:
        status = "FAIL"
        issues.append("Missing Title")
    if not meta_desc:
        status = "FAIL"
        issues.append("Missing Description")
    if not canonical:
        issues.append("Missing Canonical Link")
    if h1s == 0:
        status = "FAIL"
        issues.append("Missing H1")
    elif h1s > 1:
        issues.append("Multiple H1s")
    if not has_schema and tier in ["Tier 1", "Tier 2", "Tier 3"]:
        issues.append("No Structured Data")
    if total_imgs > 0 and alt_imgs < total_imgs:
        issues.append(f"Image Alt Gap ({alt_imgs}/{total_imgs})")

    notes = "; ".join(issues) if issues else "All baseline SEO checks pass"

    seo_rows.append([
        rel_path, tier, title[:60], len(title), meta_desc[:80] + ("..." if len(meta_desc) > 80 else ""), len(meta_desc),
        canonical, robots, h1s, h2s, f"{alt_imgs}/{total_imgs}", "Yes" if has_schema else "No", status, notes
    ])

csv_out = os.path.join(base_dir, "audit-results", "SEO_PAGE_REGISTER.csv")
with open(csv_out, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Page Route", "Tier", "Page Title", "Title Length", "Meta Description", "Desc Length",
        "Canonical URL", "Robots Directive", "H1 Count", "H2 Count", "Alt Tag Coverage", "Schema JSON-LD", "Status", "Audit Notes"
    ])
    for row in seo_rows:
        writer.writerow(row)

print(f"Audited {len(seo_rows)} pages and saved SEO_PAGE_REGISTER.csv")
