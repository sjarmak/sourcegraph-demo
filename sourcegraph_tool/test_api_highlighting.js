const axios = require('axios');

async function testAPIHighlighting() {
    console.log('🧪 Testing API highlighting functionality...');
    
    try {
        // Test 1: Search for "amazing" to find the amp article
        console.log('🔍 Searching for "amazing"...');
        const response1 = await axios.get('http://192.168.1.144:8000/api/insights?q=amazing');
        
        const ampArticle = response1.data.find(item => 
            item.title.includes('amazing AI coding assistant')
        );
        
        if (ampArticle) {
            console.log('✅ Found "Amp is an amazing AI coding assistant" article');
            console.log(`📝 Title: ${ampArticle.title}`);
            console.log(`🔗 Link: ${ampArticle.link || 'NO LINK'}`);
            console.log(`📄 Snippet: ${ampArticle.snippet?.substring(0, 100)}...`);
            
            // Check if highlighting is present
            if (ampArticle.snippet && ampArticle.snippet.includes('<mark>')) {
                console.log('✅ Snippet contains <mark> highlighting tags');
                const markCount = (ampArticle.snippet.match(/<mark>/g) || []).length;
                console.log(`🎯 Found ${markCount} highlighted terms`);
                
                // Verify it's the "amazing" word that's highlighted
                if (ampArticle.snippet.includes('<mark>amazing</mark>')) {
                    console.log('✅ The word "amazing" is properly highlighted');
                } else {
                    console.log('❌ The word "amazing" is not highlighted as expected');
                }
            } else {
                console.log('❌ No highlighting found in snippet');
            }
            
            // Check the link issue
            if (ampArticle.link) {
                console.log('✅ Article has a link - link issue is fixed');
            } else {
                console.log('❌ Article still has no link - this is the issue we were trying to fix');
            }
        } else {
            console.log('❌ Could not find the specific amp article');
        }
        
        // Test 2: Search for "amp" to see broader results
        console.log('\n🔍 Searching for "amp"...');
        const response2 = await axios.get('http://192.168.1.144:8000/api/insights?q=amp');
        
        const highlightedResults = response2.data.filter(item => 
            item.snippet && item.snippet.includes('<mark>')
        );
        
        console.log(`✅ Found ${highlightedResults.length} results with highlighting out of ${response2.data.length} total results`);
        
        if (highlightedResults.length > 0) {
            console.log('📄 Sample highlighted snippets:');
            highlightedResults.slice(0, 3).forEach((result, index) => {
                const snippet = result.snippet.substring(0, 150);
                console.log(`   ${index + 1}. ${snippet}...`);
            });
        }
        
        // Test 3: Context snippet length analysis
        const contextResults = response2.data.filter(item => item.snippet);
        if (contextResults.length > 0) {
            const avgWords = contextResults.reduce((sum, item) => {
                const wordCount = item.snippet.split(/\s+/).length;
                return sum + wordCount;
            }, 0) / contextResults.length;
            
            console.log(`📊 Average snippet length: ${Math.round(avgWords)} words`);
            
            if (avgWords >= 40 && avgWords <= 120) {
                console.log('✅ Snippet lengths appear appropriate (40-120 word range)');
            } else {
                console.log(`⚠️ Snippet lengths may need adjustment (current average: ${Math.round(avgWords)} words)`);
            }
        }
        
        console.log('\n✅ API highlighting test completed');
        
    } catch (error) {
        console.error('❌ Test failed:', error.message);
    }
}

// Add axios if it doesn't exist
try {
    require('axios');
} catch (e) {
    console.log('Installing axios...');
    require('child_process').execSync('npm install axios', { stdio: 'inherit' });
}

testAPIHighlighting().catch(console.error);
