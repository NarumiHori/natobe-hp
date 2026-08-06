import pkg from '/home/narumi/.npm-global/lib/node_modules/playwright-core/index.js';

const { chromium } = pkg;
const resourceUrl = 'https://natobe.pages.dev/';
const urls = [resourceUrl, 'https://natobe.pages.dev/company.html'];

const browser = await chromium.connectOverCDP('http://127.0.0.1:9581');
const context = browser.contexts()[0] ?? await browser.newContext();
const page = context.pages()[0] ?? await context.newPage();

for (const url of urls) {
  try {
    await page.goto(
      `https://search.google.com/search-console?resource_id=${encodeURIComponent(resourceUrl)}`,
    );
    await page.waitForTimeout(7_000);

    const urlInspectionBox = page
      .locator('input[aria-label*="URL"], input[placeholder*="URL"]')
      .first();
    await urlInspectionBox.click();
    await urlInspectionBox.fill(url);
    await urlInspectionBox.press('Enter');
    await page.waitForTimeout(20_000);

    const requestButtons = page.getByText('インデックス登録をリクエスト', { exact: true });
    const buttonCount = await requestButtons.count();
    for (let index = 0; index < buttonCount; index += 1) {
      const button = requestButtons.nth(index);
      if (await button.isVisible()) {
        await button.click();
        break;
      }
    }

    let result = 'UNKNOWN';
    for (let attempt = 0; attempt < 12; attempt += 1) {
      await page.waitForTimeout(10_000);
      const bodyText = await page.locator('body').innerText();
      if (bodyText.includes('リクエスト済み')) {
        result = 'OK';
        break;
      }
      if (bodyText.includes('割り当て量を超えています')) {
        result = 'QUOTA';
        break;
      }
    }

    console.log('[RESULT]', url, result);
  } catch (error) {
    console.error('[ERROR]', url, error);
    console.log('[RESULT]', url, 'UNKNOWN');
  }
}

try {
  await page.screenshot({ path: `/tmp/gsc-reindex-${Date.now()}.png` });
} catch (error) {
  console.error('[ERROR] screenshot', error);
}

process.exit(0);
