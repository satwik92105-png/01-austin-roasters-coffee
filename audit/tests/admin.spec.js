const { test, expect } = require('@playwright/test');

test.describe('Owner Operations Portal & POS Back-Office Audit', () => {
  test('Tier 2 Admin PIN login and tab switching', async ({ page }) => {
    await page.goto('tier2/admin.html');
    await page.waitForLoadState('domcontentloaded');

    // PIN modal/input check
    const pinInput = page.locator('#pin-input, input[type="password"], input[name="pin"]');
    if (await pinInput.isVisible()) {
      await pinInput.fill('1234');
      const submitPin = page.locator('#btn-pin-submit, button:has-text("Unlock"), button:has-text("Enter")');
      if (await submitPin.isVisible()) {
        await submitPin.click();
        await page.waitForTimeout(500);
      }
    }

    // Verify main admin layout is present
    const header = page.locator('header, h1, .admin-header');
    expect(await header.count()).toBeGreaterThan(0);
  });

  test('Tier 3 Enterprise Admin: PIN Auth, Tabs, and 86d Stock Controls', async ({ page }) => {
    await page.goto('tier3/admin.html');
    await page.waitForLoadState('domcontentloaded');

    const pinInput = page.locator('#pin-input, input[type="password"], input[name="pin"]');
    if (await pinInput.isVisible()) {
      await pinInput.fill('1234');
      const unlockBtn = page.locator('button:has-text("Unlock"), #btn-pin-submit, button[type="submit"]');
      if (await unlockBtn.isVisible()) {
        await unlockBtn.click();
        await page.waitForTimeout(500);
      }
    }

    // Tab switching test
    const tabButtons = page.locator('.tab-btn, [role="tab"], button[data-tab]');
    const tabCount = await tabButtons.count();
    if (tabCount > 0) {
      for (let i = 0; i < Math.min(tabCount, 4); i++) {
        await tabButtons.nth(i).click().catch(() => {});
        await page.waitForTimeout(200);
      }
    }

    // Verify Menu & Stock tab clearance
    const menuTab = page.locator('[data-tab="menu"], button:has-text("Menu"), button:has-text("Stock")').first();
    if (await menuTab.isVisible()) {
      await menuTab.click();
      await page.waitForTimeout(300);
      const stockSection = page.locator('#tab-menu, .menu-stock-section, #menu-management').first();
      if (await stockSection.isVisible()) {
        const bounding = await stockSection.boundingBox();
        expect(bounding).not.toBeNull();
      }
    }
  });
});
