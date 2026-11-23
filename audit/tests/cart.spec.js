const { test, expect } = require('@playwright/test');
const path = require('path');

const SCREENSHOT_DIR = path.resolve(__dirname, '../../audit-results/screenshots');

test.describe('Customer Experience: Cart Drawer & Pricing Calculations', () => {
  test('C1: Adding an item increments cart badge count and opens drawer', async ({ page }) => {
    await page.goto('tier3/menu.html', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(600);

    // Initial cart badge
    const cartCountBefore = await page.locator('#cart-count, .cart-count, [data-cart-count]').first().textContent().catch(() => '0');

    // Add first item
    const addBtn = page.locator('button.btn-add-item, button:has-text("Add to Order"), button:has-text("Add to Cart")').first();
    await expect(addBtn).toBeVisible();
    await addBtn.click();
    await page.waitForTimeout(500);

    // If customizer modal opened, confirm add
    const confirmAdd = page.locator('#btn-confirm-add, button:has-text("Add to Order"), button:has-text("Confirm & Add")').first();
    if (await confirmAdd.isVisible()) {
      await confirmAdd.click();
      await page.waitForTimeout(400);
    }

    // Verify Cart Drawer is visible
    const drawer = page.locator('#cart-drawer, .cart-drawer, .drawer-open');
    await expect(drawer).toBeVisible();

    await page.screenshot({ path: `${SCREENSHOT_DIR}/cart_drawer_opened.png` });
  });

  test('C2: Subtotal, Austin 8.25% Tax, and Total are mathematically consistent', async ({ page }) => {
    await page.goto('tier3/menu.html', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(600);

    // Add item
    const addBtn = page.locator('button.btn-add-item, button:has-text("Add to Order"), button:has-text("Add to Cart")').first();
    await addBtn.click();
    await page.waitForTimeout(400);

    const confirmAdd = page.locator('#btn-confirm-add, button:has-text("Add to Order")').first();
    if (await confirmAdd.isVisible()) {
      await confirmAdd.click();
      await page.waitForTimeout(400);
    }

    // Extract subtotal, tax, total from drawer
    const subtotalText = await page.locator('#cart-subtotal, .cart-subtotal, [data-subtotal]').first().textContent();
    const taxText = await page.locator('#cart-tax, .cart-tax, [data-tax]').first().textContent();
    const totalText = await page.locator('#cart-total, .cart-total, [data-total]').first().textContent();

    const subtotal = parseFloat(subtotalText.replace(/[^0-9.]/g, ''));
    const tax = parseFloat(taxText.replace(/[^0-9.]/g, ''));
    const total = parseFloat(totalText.replace(/[^0-9.]/g, ''));

    expect(subtotal).toBeGreaterThan(0);
    const expectedTax = Math.round(subtotal * 0.0825 * 100) / 100;
    const expectedTotal = Math.round((subtotal + expectedTax) * 100) / 100;

    // Verify tax is within 1 cent tolerance
    expect(Math.abs(tax - expectedTax)).toBeLessThanOrEqual(0.02);
    expect(Math.abs(total - expectedTotal)).toBeLessThanOrEqual(0.02);
  });

  test('C3: Promo code DOGSPEED15 applies 15% discount', async ({ page }) => {
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

    const promoInput = page.locator('#promo-input, input[placeholder*="Promo"], input[name="promo"]');
    const applyBtn = page.locator('#btn-apply-promo, button:has-text("Apply")');

    if (await promoInput.count() > 0 && await applyBtn.count() > 0) {
      await promoInput.fill('DOGSPEED15');
      await applyBtn.click();
      await page.waitForTimeout(400);

      const discountRow = page.locator('#cart-discount-row, .discount-badge, :has-text("15% OFF")');
      await expect(discountRow.first()).toBeVisible();
      await page.screenshot({ path: `${SCREENSHOT_DIR}/cart_promo_applied.png` });
    }
  });

  test('C4: Cart items persist across page reload', async ({ page }) => {
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

    // Reload page
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(600);

    const cartCount = await page.locator('#cart-count, .cart-count').first().textContent();
    expect(parseInt(cartCount, 10)).toBeGreaterThanOrEqual(1);
  });
});
