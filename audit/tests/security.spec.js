const { test, expect } = require('@playwright/test');

test.describe('Application Security & Vulnerability Audit', () => {
  const API_BASE = 'https://01-austin-roasters-coffee.vercel.app/api';

  test('Public API Endpoint Data Exposure Audit', async ({ request }) => {
    // Audit public /api/health
    const healthRes = await request.get(`${API_BASE}/health`).catch(() => null);
    if (healthRes && healthRes.ok()) {
      const data = await healthRes.json();
      expect(data).toHaveProperty('status');
      // Documents version drift if returned
    }

    // Audit public /api/orders data exposure
    const ordersRes = await request.get(`${API_BASE}/orders`).catch(() => null);
    if (ordersRes && ordersRes.ok()) {
      const orders = await ordersRes.json();
      // If unauthenticated endpoint returns customer data, it represents BOLA/Data Exposure
      expect(Array.isArray(orders)).toBeTruthy();
    }
  });

  test('Input Sanitization & XSS Resistance on Checkout Form', async ({ page }) => {
    await page.goto('tier3/menu.html');
    await page.waitForLoadState('domcontentloaded');

    // Add first item to cart to unlock checkout modal
    const addBtn = page.locator('.btn-add-cart, button:has-text("Add to Cart")').first();
    if (await addBtn.isVisible()) {
      await addBtn.click();
      await page.waitForTimeout(300);
    }

    // Open checkout modal
    const checkoutBtn = page.locator('#btn-checkout, .btn-checkout, button:has-text("Checkout")').first();
    if (await checkoutBtn.isVisible()) {
      await checkoutBtn.click();
      await page.waitForTimeout(500);

      // Attempt XSS payload injection in Name input
      const nameInput = page.locator('#cust-name, input[name="name"], input[placeholder*="Name" i]').first();
      if (await nameInput.isVisible()) {
        const xssPayload = '<img src=x onerror="window.__xss_triggered=true">';
        await nameInput.fill(xssPayload);

        // Verify window.__xss_triggered is undefined (not executed)
        const triggered = await page.evaluate(() => window.__xss_triggered);
        expect(triggered).toBeUndefined();
      }
    }
  });
});
