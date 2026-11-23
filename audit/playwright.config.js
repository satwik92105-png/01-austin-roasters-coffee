const { defineConfig } = require('@playwright/test');
const path = require('path');

module.exports = defineConfig({
  testDir: './tests',
  timeout: 45000,
  expect: {
    timeout: 10000
  },
  fullyParallel: false,
  retries: 0,
  workers: 1,
  reporter: [
    ['list'],
    ['json', { outputFile: path.resolve(__dirname, '../audit-results/test-results.json') }],
    ['html', { outputFolder: path.resolve(__dirname, '../audit-results/playwright-report'), open: 'never' }]
  ],
  use: {
    channel: 'chrome',
    headless: true,
    viewport: { width: 1280, height: 800 },
    ignoreHTTPSErrors: true,
    video: 'off',
    screenshot: 'on',
    trace: 'retain-on-failure',
    baseURL: 'https://satwik92105-png.github.io/01-austin-roasters-coffee/',
  },
});
