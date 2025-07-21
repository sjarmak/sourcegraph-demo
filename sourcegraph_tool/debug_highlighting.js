// Debug highlighting function
const highlightText = (text, query) => {
  if (!query || !text) return text;
  
  console.log('Input text:', text.substring(0, 100));
  console.log('Search query:', query);
  
  // Split query into individual words and filter out short words
  const keywords = query.toLowerCase().split(/\s+/).filter(k => k.length > 2);
  console.log('Keywords after filtering:', keywords);
  
  let highlightedText = text;
  
  keywords.forEach(keyword => {
    console.log(`Processing keyword: "${keyword}"`);
    
    // Escape special regex characters
    const escapedKeyword = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    
    // Use a simple global case-insensitive match without word boundaries
    const regex = new RegExp(`(${escapedKeyword})`, 'gi');
    
    console.log(`Regex: ${regex}`);
    
    const matches = text.match(regex);
    console.log(`Matches found:`, matches);
    
    highlightedText = highlightedText.replace(regex, '<strong class="bg-yellow-200 px-1 rounded">$1</strong>');
  });
  
  return highlightedText;
};

// Test cases based on the actual search results that contain "Amp"
const testCases = [
  {
    text: `Built an AI Agent in n8n for YouTube Market Analysis – Great for Content Creators!png?width=1920&amp;format=png&amp;auto=webp&amp;s=dd788d8ebfe15a113d6bcd973cba8162c95fcfc3`,
    query: "Amp"
  },
  {
    text: `Serverless Scaling: Deploying Strands + MCP on AWS—Lambda (native &amp; web adapter) and Fargate`,
    query: "Amp"  
  },
  {
    text: `All AI Coding Agents You KnowHere are a few examples to give you a sense of the range: Cursor (AI-native IDE) IDX/Firebase Studio (Google's web IDE) Replit Framework`,
    query: "Amp"
  }
];

testCases.forEach((testCase, index) => {
  console.log(`\n=== Test Case ${index + 1} ===`);
  const result = highlightText(testCase.text, testCase.query);
  console.log('Highlighted text contains <strong>:', result.includes('<strong>'));
  console.log('Result preview:', result.substring(0, 150) + '...');
});
