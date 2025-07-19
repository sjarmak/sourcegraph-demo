// Simple test to check if frontend can connect to backend API
async function testFrontendAPI() {
    console.log('Testing frontend API connection...');
    
    try {
        // Test basic API connection
        const response = await fetch('http://localhost:8000/api/insights?limit=1');
        const data = await response.json();
        console.log('✅ API connection successful');
        console.log('Sample insight:', data[0]);
        
        // Test scrape status
        const statusResponse = await fetch('http://localhost:8000/api/scrape-feeds/status');
        const statusData = await statusResponse.json();
        console.log('✅ Scrape status:', statusData);
        
        // Test CORS
        console.log('✅ CORS working - no errors');
        
    } catch (error) {
        console.error('❌ Error:', error);
    }
}

testFrontendAPI();
