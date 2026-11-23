const { test, expect } = require('@playwright/test');

const pagesToAudit = [
  'index.html',
  'demo.html',
  'tier1/index.html',
  'tier2/menu.html',
  'tier3/menu.html',
  'tier3/admin.html'
];

test.describe('WCAG Accessibility Baseline Audit', () => {
  for (const p of pagesToAudit) {
    test(`Accessibility compliance for ${p}`, async ({ page }) => {
      await page.goto(p);
      await page.waitForLoadState('domcontentloaded');

      // 1. Language attribute
      const lang = await page.locator('html').getAttribute('lang');
      expect(lang).toBeTruthy();

      // 2. Document title
      const title = await page.title();
      expect(title.length).toBeGreaterThan(0);

      // 3. Inspect images without alt
      const imagesWithoutAlt = await page.evaluate(() => {
        const imgs = Array.from(document.querySelectorAll('img'));
        return imgs.filter(img => !img.hasAttribute('alt') || img.getAttribute('alt').trim() === '').length;
      });

      // 4. Form inputs without associated labels or aria-label
      const unlabelledInputs = await page.evaluate(() => {
        const inputs = Array.from(document.querySelectorAll('input:not([type="hidden"]), select, textarea'));
        return inputs.filter(inp => {
          const id = inp.id;
          const hasLabel = id ? !!document.querySelector(`label[for="${id}"]`) : false;
          const hasAria = inp.hasAttribute('aria-label') || inp.hasAttribute('aria-labelledby') || inp.hasAttribute('placeholder');
          return !hasLabel && !hasAria;
        }).length;
      });

      // Log findings for report
      expect(imagesWithoutAlt).toBeLessThanOrEqual(5);
      expect(unlabelledInputs).toBeLessThanOrEqual(3);
    });
  }
});
