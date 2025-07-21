const { chromium } = require('playwright');

async function testFrontend() {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    console.log('Navigating to http://192.168.1.144:3000/...');
    await page.goto('http://192.168.1.144:3000/', { waitUntil: 'networkidle' });
    
    // Take a screenshot
    await page.screenshot({ path: 'frontend_screenshot.png' });
    console.log('Screenshot saved as frontend_screenshot.png');
    
    // Get page title and content
    const title = await page.title();
    console.log(`Page title: ${title}`);
    
    // Check if React app loaded
    const reactRoot = await page.locator('#root').count();
    console.log(`React root element found: ${reactRoot > 0}`);
    
    // Get some basic page info
    const url = page.url();
    console.log(`Current URL: ${url}`);
    
    // Check for any console errors
    const consoleLogs = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log(`Console error: ${msg.text()}`);
        consoleLogs.push(`ERROR: ${msg.text()}`);
      }
      if (msg.type() === 'warning') {
        console.log(`Console warning: ${msg.text()}`);
        consoleLogs.push(`WARNING: ${msg.text()}`);
      }
    });
    
    // Wait a bit to see if there are any immediate errors
    await page.waitForTimeout(3000);
    
    // Click on Dashboard tab
    console.log('Clicking on Dashboard tab...');
    await page.click('text=Dashboard');
    await page.waitForTimeout(2000);
    
    // Take another screenshot after clicking Dashboard
    await page.screenshot({ path: 'dashboard_screenshot.png' });
    console.log('Dashboard screenshot saved as dashboard_screenshot.png');
    
    // Check for visible error messages on the page
    const errorElements = await page.locator('text=/error|Error|ERROR|failed|Failed|FAILED/i').count();
    if (errorElements > 0) {
      console.log(`Found ${errorElements} potential error messages on page`);
      const errorTexts = await page.locator('text=/error|Error|ERROR|failed|Failed|FAILED/i').allTextContents();
      console.log('Error messages found:', errorTexts);
    }
    
    console.log('Frontend test completed successfully!');
    
  } catch (error) {
    console.error('Error testing frontend:', error.message);
  } finally {
    await browser.close();
  }
}

testFrontend();
