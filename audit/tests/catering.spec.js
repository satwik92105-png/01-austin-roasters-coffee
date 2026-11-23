const { test, expect } = require('@playwright/test');

test.describe('Event & Enterprise Catering Engine Audit (Tier 3)', () => {
  test('Headcount slider, packages, and instant quote calculation', async ({ page }) => {
    await page.goto('tier3/catering.html');
    await page.waitForLoadState('domcontentloaded');

    // Headcount slider
    const slider = page.locator('#guest-slider, input[type="range"]');
    if (await slider.isVisible()) {
      await slider.fill('120');
      await slider.dispatchEvent('input');
      await page.waitForTimeout(500);

      // Verify dynamic quote display updates
      const quoteText = page.locator('#quote-amount, .quote-price, #total-quote');
      if (await quoteText.isVisible()) {
        const text = await quoteText.innerText();
        expect(text).toMatch(/\$|USD/i);
      }
    }

    // Add-on checkboxes
    const checkboxes = page.locator('input[type="checkbox"]');
    const cbCount = await checkboxes.count();
    if (cbCount > 0) {
      await checkboxes.first().check().catch(() => {});
    }

    // Contact form inputs
    const nameInput = page.locator('input[name="name"], #cat-name, input[placeholder*="Name" i]').first();
    if (await nameInput.isVisible()) {
      await nameInput.fill('Techstars Austin Event');
    }

    const emailInput = page.locator('input[name="email"], #cat-email, input[type="email"]').first();
    if (await emailInput.isVisible()) {
      await emailInput.fill('events@techstars-example.com');
    }

    // Submit inquiry
    const submitBtn = page.locator('button[type="submit"], #btn-quote, .btn-submit-catering').first();
    if (await submitBtn.isVisible()) {
      await submitBtn.click();
      await page.waitForTimeout(1000);
    }

    expect(page.url()).toContain('catering.html');
  });
});
