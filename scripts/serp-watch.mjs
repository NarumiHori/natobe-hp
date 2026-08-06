import pkg from '/home/narumi/.npm-global/lib/node_modules/playwright-core/index.js';

const { chromium } = pkg;
const searchUrl = 'https://www.google.com/search?q=%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE%E3%83%8A%E3%83%88%E3%83%93%E3%83%BC&hl=ja&gl=jp';
const screenshotPath = process.argv[2] ?? '/tmp/serp-watch.png';

let page;
let result = { found: false };

try {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9581');
  const context = browser.contexts()[0] ?? await browser.newContext();
  page = await context.newPage();

  await page.goto(searchUrl, {
    waitUntil: 'domcontentloaded',
    timeout: 60_000,
  });
  await page.waitForTimeout(3_000);

  const link = page.locator('div#search a[href*="natobe.pages.dev"]').first();
  if (await link.count() > 0) {
    const block = link.locator('xpath=ancestor::div[@data-hveid][1]');
    if (await block.count() > 0) {
      const raw = (await block.innerText()).trim();
      const heading = block.locator('h3').first();
      const title = await heading.count() > 0 ? (await heading.innerText()).trim() : '';
      const lines = raw.split('\n').map((line) => line.trim()).filter(Boolean);
      const titleLineIndex = lines.findIndex((line) => line === title);
      const snippet = (titleLineIndex >= 0 ? lines.slice(titleLineIndex + 1) : lines.slice(1)).join('\n');

      result = {
        siteName: lines[0] ?? '',
        title,
        snippet,
        foundAt: new Date().toISOString(),
        raw,
      };
    }
  }
} catch (error) {
  console.error('[ERROR] SERP inspection failed:', error);
} finally {
  if (page) {
    try {
      await page.screenshot({ path: screenshotPath });
    } catch (error) {
      console.error('[ERROR] screenshot failed:', error);
    }

    try {
      await page.close();
    } catch (error) {
      console.error('[ERROR] page close failed:', error);
    }
  }

  process.stdout.write(`${JSON.stringify(result)}\n`);
  process.exit(0);
}
