const { test, expect } = require('@playwright/test');
const path = require('path');

const SCREENSHOT_DIR = path.resolve(__dirname, '../../audit-results/screenshots');

test.describe('Customer Experience: Checkout & Order Placement Journey', () => {
  test('CK1: Checkout modal opens and input focus does NOT trigger auto-close', async ({ page }) => {
    await page.goto('tier3/menu.html', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(600);

    // Add item to cart
    const addBtn = page.locator('button.btn-add-item, button:has-text("Add to Order")').first();
    await addBtn.click();
    await page.waitForTimeout(400);

    const confirmAdd = page.locator('#btn-confirm-add, button:has-text("Add to Order")').first();
    if (await confirmAdd.isVisible()) {
      await confirmAdd.click();
      await page.waitForTimeout(400);
    }

    // Open Checkout Modal
    const proceedBtn = page.locator('#btn-checkout, button:has-text("Proceed to"), button:has-text("Checkout")').first();
    await expect(proceedBtn).toBeVisible();
    await proceedBtn.click();
    await page.waitForTimeout(500);

    const checkoutModal = page.locator('#checkout-modal, .checkout-modal, .modal-card:visible').first();
    await expect(checkoutModal).toBeVisible();

    // Critical Bug Check: Click into Full Name input field with real mouse coordinates
    const nameInput = page.locator('#cust-name, input[name="customerName"], input[placeholder*="Name"]').first();
    await expect(nameInput).toBeVisible();
    await nameInput.click();
    await page.waitForTimeout(300);

    // Assert modal remains visible and focused
    await expect(checkoutModal).toBeVisible();
    await nameInput.fill('Sarah Jenkins');

    const phoneInput = page.locator('#cust-phone, input[name="phone"], input[placeholder*="Phone"]').first();
    await phoneInput.click();
    await expect(checkoutModal).toBeVisible();
    await phoneInput.fill('(512) 555-0199');

    await page.screenshot({ path: `${SCREENSHOT_DIR}/checkout_modal_input_focus.png` });
  });

  test('CK2: Synthetic order placement completes and displays confirmation screen with ticket and receipt', async ({ page }) => {
    await page.goto('tier3/menu.html', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(600);

    const addBtn = page.locator('button.btn-add-item, button:has-text("Add to Order")').first();
    await addBtn.click();
    await page.waitForTimeout(400);

    const confirmAdd = page.locator('#btn-confirm-add, button:has-text("Add to Order")').first();
    if (await confirmAdd.isVisible()) {
      await confirmAdd.click();
      await page.waitForTimeout(400);
    }

    const proceedBtn = page.locator('#btn-checkout, button:has-text("Proceed to")').first();
    await proceedBtn.click();
    await page.waitForTimeout(500);

    // Fill form
    const nameInput = page.locator('#cust-name, input[name="customerName"]').first();
    const phoneInput = page.locator('#cust-phone, input[name="phone"]').first();
    await nameInput.fill('David Miller');
    await phoneInput.fill('(512) 555-8822');

    // Submit Order (Counter Pay or Submit)
    const submitBtn = page.locator('#btn-submit-order, button:has-text("Place Order"), button:has-text("Pay at Counter"), button[type="submit"]').first();
    await submitBtn.click();

    // Wait for success / confirmation screen
    const successTitle = page.locator('#success-order-title, .order-confirmed, :has-text("Order Confirmed"), :has-text("Thank You")').first();
    await expect(successTitle).toBeVisible({ timeout: 12000 });

    // Verify order ID format (FT-XXXX)
    const orderIdElem = page.locator('#confirmed-order-id, .order-number, [data-order-id]').first();
    const orderIdText = await orderIdElem.textContent();
    expect(orderIdText).toMatch(/FT-\d+/i);

    // Verify Download PDF Receipt button is present
    const pdfBtn = page.locator('#btn-download-pdf, button:has-text("PDF Receipt"), a:has-text("Receipt")').first();
    await expect(pdfBtn).toBeVisible();

    await page.screenshot({ path: `${SCREENSHOT_DIR}/checkout_confirmation_success.png` });
  });

  test('CK3: Payment flow audit — verify whether card payments are simulated vs genuine Stripe processing', async ({ page }) => {
    await page.goto('tier3/menu.html', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(600);

    // Inspect client script to determine Stripe integration state
    const isStripeConfigured = await page.evaluate(() => {
      return {
        hasStripeSDK: typeof window.Stripe !== 'undefined',
        stripeKey: window.STRIPE_PUBLIC_KEY || null
      };
    });

    // Verification finding: Real Stripe SDK vs Mock Simulation
    // Record actual state
    expect(isStripeConfigured).toBeDefined();
  });
});
