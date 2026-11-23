const { test, expect } = require('@playwright/test');
const path = require('path');

const SCREENSHOT_DIR = path.resolve(__dirname, '../../audit-results/screenshots');

test.describe('Customer Experience: Homepage & Landing Experience', () => {
  test('A1: Master Agency Hub loads with correct title, brand identity and 3 tiers', async ({ page }) => {
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') consoleErrors.push(msg.text());
    });

    await page.goto('index.html', { waitUntil: 'domcontentloaded' });
    await expect(page).toHaveTitle(/Agency Sales Hub/i);

    // Check header & brand
    const logo = page.locator('.brand-logo');
    await expect(logo).toBeVisible();
    await expect(logo).toContainText('FLAT TRACK');

    // Check Hero H1
    const h1 = page.locator('h1');
    await expect(h1).toBeVisible();
    await expect(h1).toContainText('Austin Coffee Lovers');

    // Check 3 Tier Cards
    const tierCards = page.locator('.tier-card');
    await expect(tierCards).toHaveCount(3);

    // Check 28-row matrix
    const matrixRows = page.locator('table tbody tr');
    const rowCount = await matrixRows.count();
    expect(rowCount).toBe(28);

    await page.screenshot({ path: `${SCREENSHOT_DIR}/homepage_agency_hub.png`, fullPage: false });
  });

  test('A2: Standalone Client Demo Page loads with 3 luxury roastery cards & amenities', async ({ page }) => {
    await page.goto('demo.html', { waitUntil: 'domcontentloaded' });
    await expect(page).toHaveTitle(/Client Demo & Amenities/i);

    const brand = page.locator('.demo-brand');
    await expect(brand).toBeVisible();
    await expect(brand).toContainText('Flat Track Coffee Roasters');

    const cards = page.locator('.demo-tier-card');
    await expect(cards).toHaveCount(3);

    // Check Tier 1, 2, 3 prices
    await expect(page.locator('.demo-card-price').nth(0)).toContainText('$500');
    await expect(page.locator('.demo-card-price').nth(1)).toContainText('$1,500');
    await expect(page.locator('.demo-card-price').nth(2)).toContainText('$2,000');

    // Check 28-row matrix
    const matrixRows = page.locator('.demo-matrix-table tbody tr');
    expect(await matrixRows.count()).toBe(28);

    await page.screenshot({ path: `${SCREENSHOT_DIR}/homepage_client_demo.png`, fullPage: false });
  });

  test('A3: Tier 1 Brand Showcase single-page loads with Austin CST status & filter menu', async ({ page }) => {
    await page.goto('tier1/index.html', { waitUntil: 'domcontentloaded' });
    await expect(page).toHaveTitle(/Flat Track Coffee Roasters/i);

    // Check Open/Closed status badge
    const statusBadge = page.locator('#austin-status, .status-indicator, .status-badge').first();
    await expect(statusBadge).toBeVisible();

    // Check Category filter buttons
    const filterBtns = page.locator('.filter-btn, .category-pill, .menu-tab');
    expect(await filterBtns.count()).toBeGreaterThanOrEqual(4);

    await page.screenshot({ path: `${SCREENSHOT_DIR}/tier1_brand_showcase.png`, fullPage: false });
  });

  test('A4: Tier 3 Flagship Storefront loads with cinematic hero & 3D timeline', async ({ page }) => {
    await page.goto('tier3/index.html', { waitUntil: 'domcontentloaded' });
    await expect(page).toHaveTitle(/Flat Track/i);

    const hero = page.locator('section').first();
    await expect(hero).toBeVisible();

    // Check navigation links
    const navLinks = page.locator('nav a, header a');
    expect(await navLinks.count()).toBeGreaterThanOrEqual(4);

    await page.screenshot({ path: `${SCREENSHOT_DIR}/tier3_flagship_home.png`, fullPage: false });
  });
});
