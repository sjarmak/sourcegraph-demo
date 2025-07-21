const { chromium } = require('playwright');

async function testSearchHighlighting() {
  const browser = await chromium.launch({ headless: false }); // Show browser for debugging
  const page = await browser.newPage();
  
  try {
    console.log('Navigating to frontend...');
    await page.goto('http://192.168.1.144:3000/', { waitUntil: 'networkidle' });
    
    // Wait for the page to load
    await page.waitForSelector('#root', { timeout: 10000 });
    console.log('Frontend loaded successfully');
    
    // Take a screenshot to see what's on the page
    await page.screenshot({ path: 'initial_page.png' });
    console.log('Initial page screenshot saved');
    
    // Navigate to insights page if not already there
    const insightsLink = page.locator('a[href="/insights"]');
    if (await insightsLink.count() > 0) {
      console.log('Clicking on Insights tab...');
      await insightsLink.click();
      await page.waitForTimeout(2000);
    }
    
    // Look for search input with placeholder "Search insights..."
    console.log('Looking for search input...');
    const searchInput = page.locator('input[placeholder="Search insights..."]');
    
    // Debug: check what inputs are available
    const allInputs = page.locator('input');
    const inputCount = await allInputs.count();
    console.log(`Found ${inputCount} input elements on page`);
    
    for (let i = 0; i < Math.min(inputCount, 5); i++) {
      const input = allInputs.nth(i);
      const placeholder = await input.getAttribute('placeholder');
      const type = await input.getAttribute('type');
      console.log(`Input ${i}: type="${type}", placeholder="${placeholder}"`);
    }
    
    await searchInput.waitFor({ timeout: 5000 });
    
    console.log('Searching for "Amp"...');
    await searchInput.fill('Amp');
    
    // Look for search button or trigger search
    const searchButton = page.locator('button').filter({ hasText: /search/i }).first();
    if (await searchButton.count() > 0) {
      await searchButton.click();
    } else {
      // Try pressing Enter
      await searchInput.press('Enter');
    }
    
    // Wait for search results to load
    await page.waitForTimeout(3000);
    
    // Take a screenshot of search results
    await page.screenshot({ path: 'search_amp_results.png', fullPage: true });
    console.log('Search results screenshot saved');
    
    // Find all search result items - ModernInsightCard uses specific card styling
    const resultItems = page.locator('[class*="bg-white"][class*="border"][class*="rounded-lg"]').filter({ has: page.locator('h3') });
    const resultCount = await resultItems.count();
    console.log(`Found ${resultCount} search result items`);
    
    if (resultCount > 0) {
      // Check first few results for highlighting
      const maxResults = Math.min(5, resultCount);
      for (let i = 0; i < maxResults; i++) {
        const resultItem = resultItems.nth(i);
        const resultText = await resultItem.textContent();
        
        console.log(`\n--- Result ${i + 1} ---`);
        console.log('Full text:', resultText?.substring(0, 200) + '...');
        
        // Check for highlighted text - the code uses bg-yellow-200 class in strong tags
        const highlightedElements = resultItem.locator('strong[class*="bg-yellow-200"], mark, .highlight, .highlighted');
        const highlightCount = await highlightedElements.count();
        console.log(`Highlighted elements found: ${highlightCount}`);
        
        if (highlightCount > 0) {
          for (let j = 0; j < highlightCount; j++) {
            const highlightText = await highlightedElements.nth(j).textContent();
            console.log(`Highlight ${j + 1}: "${highlightText}"`);
          }
        }
        
        // Check if "Amp" appears in the text (case insensitive)
        const ampMatches = (resultText?.match(/amp/gi) || []).length;
        console.log(`"Amp" occurrences: ${ampMatches}`);
        
        // Check if it's just in URLs
        const urlMatches = (resultText?.match(/https?:\/\/[^\s]*amp[^\s]*/gi) || []).length;
        console.log(`"Amp" in URLs: ${urlMatches}`);
        console.log(`"Amp" in content (non-URL): ${ampMatches - urlMatches}`);
      }
    } else {
      console.log('No search results found for "Amp"');
    }
    
    // Check the search implementation in the page
    console.log('\n--- Checking search implementation ---');
    const searchFunctions = await page.evaluate(() => {
      // Look for search-related functions in the global scope
      const searchRelated = [];
      for (const key in window) {
        if (key.toLowerCase().includes('search') || key.toLowerCase().includes('highlight')) {
          searchRelated.push(key);
        }
      }
      return searchRelated;
    });
    console.log('Search-related functions found:', searchFunctions);
    
  } catch (error) {
    console.error('Error during search highlighting test:', error);
    await page.screenshot({ path: 'search_error.png' });
  } finally {
    // Keep browser open for manual inspection
    console.log('\nTest completed. Browser will stay open for 30 seconds for manual inspection...');
    await page.waitForTimeout(30000);
    await browser.close();
  }
}

testSearchHighlighting();
