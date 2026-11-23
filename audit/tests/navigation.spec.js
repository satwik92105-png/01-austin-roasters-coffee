const { test, expect } = require('@playwright/test');
const path = require('path');

const SCREENSHOT_DIR = path.resolve(__dirname, '../../audit-results/screenshots');

test.describe('Customer Experience: Site Navigation & Link Integrity', () => {
  test('N1: Navigation links across Tier 3 suite resolve without 404', async ({ page }) => {
    const brokenLinks = [];
    page.on('response', response => {
      if (response.status() >= 400 && response.url().includes('satwik92105-png.github.io')) {
        brokenLinks.push(`${response.status()} ${response.url()}`);
      }
    });

    await page.goto('tier3/index.html', { waitUntil: 'domcontentloaded' });

    // Test Menu link
    const menuLink = page.locator('header a[href*="menu"], nav a[href*="menu"]').first();
    if (await menuLink.count() > 0) {
      await menuLink.click();
      await page.waitForLoadState('domcontentloaded');
      expect(page.url()).toContain('menu.html');
    }

    // Test Reservations link
    const resLink = page.locator('header a[href*="reserve"], nav a[href*="reserve"]').first();
    if (await resLink.count() > 0) {
      await resLink.click();
      await page.waitForLoadState('domcontentloaded');
      expect(page.url()).toContain('reserve.html');
    }

    // Test Subscriptions link
    const subLink = page.locator('header a[href*="subscribe"], nav a[href*="subscribe"]').first();
    if (await subLink.count() > 0) {
      await subLink.click();
      await page.waitForLoadState('domcontentloaded');
      expect(page.url()).toContain('subscribe.html');
    }

    // Test Catering link
    const catLink = page.locator('header a[href*="catering"], nav a[href*="catering"]').first();
    if (await catLink.count() > 0) {
      await catLink.click();
      await page.waitForLoadState('domcontentloaded');
      expect(page.url()).toContain('catering.html');
    }

    expect(brokenLinks).toHaveLength(0);
  });

  test('N2: Mobile menu toggle functions on 390x844 viewport', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('tier3/index.html', { waitUntil: 'domcontentloaded' });

    const toggle = page.locator('#mobile-menu-toggle, .mobile-menu-toggle, [aria-label*="Menu"]');
    if (await toggle.count() > 0) {
      await expect(toggle).toBeVisible();
      await toggle.click();
      await page.waitForTimeout(400);

      const navDrawer = page.locator('.mobile-drawer, .mobile-nav, nav.open, .mobile-menu');
      if (await navDrawer.count() > 0) {
        await expect(navDrawer).toBeVisible();
      }
      await page.screenshot({ path: `${SCREENSHOT_DIR}/nav_mobile_drawer.png` });
    }
  });
});
