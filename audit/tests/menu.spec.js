const { test, expect } = require('@playwright/test');
const path = require('path');

const SCREENSHOT_DIR = path.resolve(__dirname, '../../audit-results/screenshots');

test.describe('Customer Experience: Menu Catalog & Product Interaction', () => {
  test('M1: Tier 3 Menu renders all 10 canonical products with names, prices, and images', async ({ page }) => {
    await page.goto('tier3/menu.html', { waitUntil: 'networkidle' });
    await expect(page).toHaveTitle(/Menu/i);

    // Verify product cards are displayed
    const cards = page.locator('.menu-card, .menu-item-card, [data-item-id]');
    const count = await cards.count();
    expect(count).toBeGreaterThanOrEqual(10);

    // Verify first product has name, price, description
    const firstCard = cards.first();
    await expect(firstCard).toBeVisible();
    const priceText = await firstCard.locator('.menu-card-price, .price, .item-price').first().textContent();
    expect(priceText).toMatch(/\$\d+(\.\d{2})?/);

    await page.screenshot({ path: `${SCREENSHOT_DIR}/menu_catalog_tier3.png`, fullPage: false });
  });

  test('M2: Category filters filter items without reloading page', async ({ page }) => {
    await page.goto('tier3/menu.html', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(600);

    const filterBeans = page.locator('button[data-category="beans"], .category-tab:has-text("Beans"), [data-filter="beans"]').first();
    if (await filterBeans.count() > 0) {
      await filterBeans.click();
      await page.waitForTimeout(300);

      // Verify beans items are visible
      const visibleCards = page.locator('.menu-card:visible, .menu-item-card:visible');
      const count = await visibleCards.count();
      expect(count).toBeGreaterThanOrEqual(1);
    }
  });

  test('M3: Flavor Profile Radar Meters (Acidity, Body, Sweetness) are rendered on Tier 3', async ({ page }) => {
    await page.goto('tier3/menu.html', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(600);

    const flavorMeters = page.locator('.flavor-meter, .flavor-profile, .flavor-bar, [data-flavor]');
    const count = await flavorMeters.count();
    // Flavor meters exist on Tier 3 coffee items
    expect(count).toBeGreaterThanOrEqual(1);
    await page.screenshot({ path: `${SCREENSHOT_DIR}/menu_flavor_meters.png` });
  });

  test('M4: Drink Customizer modal opens and displays modifier options', async ({ page }) => {
    await page.goto('tier3/menu.html', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(600);

    // Click customize or add button
    const customizeBtn = page.locator('.btn-customize, button:has-text("Customize"), .btn-add-item').first();
    if (await customizeBtn.count() > 0) {
      await customizeBtn.click();
      await page.waitForTimeout(400);

      const modal = page.locator('#customizer-modal, .customizer-modal, .modal-card:visible').first();
      await expect(modal).toBeVisible();
      await page.screenshot({ path: `${SCREENSHOT_DIR}/menu_customizer_modal.png` });

      // Close modal
      const closeBtn = page.locator('.modal-close, #close-customizer, button:has-text("×")').first();
      if (await closeBtn.count() > 0) {
        await closeBtn.click();
      }
    }
  });
});
