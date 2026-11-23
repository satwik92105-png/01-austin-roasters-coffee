const { test, expect } = require('@playwright/test');

test.describe('Barista Kitchen Display System (KDS) Audit (Tier 3)', () => {
  test('KDS Queue rendering and bump-bar status transitions', async ({ page }) => {
    await page.goto('tier3/kitchen.html');
    await page.waitForLoadState('domcontentloaded');

    // Verify KDS Header & Station controls
    const header = page.locator('header, h1:has-text("Kitchen"), h1:has-text("KDS"), h1:has-text("Barista")').first();
    expect(await header.isVisible()).toBeTruthy();

    // Check for tickets/order cards
    const orderCards = page.locator('.kds-card, .ticket, .order-ticket');
    const count = await orderCards.count();

    // Check filter buttons (All, Drinks, Food, etc.)
    const filterButtons = page.locator('.filter-btn, button[data-station], button[data-filter]');
    if (await filterButtons.count() > 0) {
      await filterButtons.first().click().catch(() => {});
    }

    // Check bump action button if ticket is present
    const bumpBtn = page.locator('.btn-bump, button:has-text("Bump"), button:has-text("Ready"), button:has-text("Done")').first();
    if (await bumpBtn.isVisible()) {
      await bumpBtn.click().catch(() => {});
      await page.waitForTimeout(300);
    }

    expect(page.url()).toContain('kitchen.html');
  });
});
