const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://127.0.0.1:5173');
  console.log('Waiting for page to load...');
  await page.waitForTimeout(5000);
  await page.screenshot({ path: '/home/jules/verification/system_status_v3.png', fullPage: true });
  console.log('Screenshot saved to /home/jules/verification/system_status_v3.png');
  await browser.close();
})();
