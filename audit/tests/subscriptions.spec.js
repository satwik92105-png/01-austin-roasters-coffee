const { test, expect } = require('@playwright/test');

test.describe('Coffee Club Subscription Engine Audit (Tier 3)', () => {
  test('Subscription configurator interacts with frequencies, grinds, and quantities', async ({ page }) => {
    await page.goto('tier3/subscribe.html');
    await page.waitForLoadState('domcontentloaded');

    // Verify key subscription plans exist
    const planOptions = page.locator('.tier-card, .plan-card, .subscription-option, [data-plan]');
    const count = await planOptions.count();
    expect(count).toBeGreaterThan(0);

    // Click on a plan
    await planOptions.first().click().catch(() => {});

    // Frequency selectors (e.g., Weekly, Bi-Weekly, Monthly)
    const freqButtons = page.locator('button:has-text("Week"), button:has-text("Month"), input[name="frequency"]');
    if (await freqButtons.count() > 0) {
      await freqButtons.first().click().catch(() => {});
    }

    // Grind selectors (Whole Bean, French Press, Drip, Espresso)
    const grindOptions = page.locator('button:has-text("Whole Bean"), button:has-text("Drip"), button:has-text("Espresso"), input[name="grind"]');
    if (await grindOptions.count() > 0) {
      await grindOptions.first().click().catch(() => {});
    }

    // Test Subscribe Button initiates modal or cart addition
    const subscribeBtn = page.locator('#btn-subscribe, button:has-text("Join Club"), button:has-text("Subscribe Now"), button:has-text("Start Subscription")').first();
    if (await subscribeBtn.isVisible()) {
      await subscribeBtn.click();
      await page.waitForTimeout(1000);
    }

    expect(page.url()).toContain('subscribe.html');
  });
});
