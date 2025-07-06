// Simple script to test if the frontend is rendering correctly
const http = require('http');

function checkEndpoint(url, callback) {
  const request = http.get(url, (response) => {
    let data = '';
    response.on('data', (chunk) => {
      data += chunk;
    });
    response.on('end', () => {
      callback(null, {
        statusCode: response.statusCode,
        contentLength: data.length,
        hasReactRoot: data.includes('id="root"'),
        hasViteClient: data.includes('@vite/client'),
        hasErrors: data.toLowerCase().includes('error'),
      });
    });
  });
  
  request.on('error', (error) => {
    callback(error);
  });
}

console.log('Testing frontend endpoints...\n');

// Test main page
checkEndpoint('http://localhost:3000', (err, result) => {
  if (err) {
    console.log('❌ Frontend not accessible:', err.message);
    return;
  }
  
  console.log('✅ Frontend main page:');
  console.log(`   Status: ${result.statusCode}`);
  console.log(`   Content length: ${result.contentLength} bytes`);
  console.log(`   Has React root: ${result.hasReactRoot}`);
  console.log(`   Has Vite client: ${result.hasViteClient}`);
  console.log(`   Has errors: ${result.hasErrors}`);
  
  if (result.statusCode === 200 && result.hasReactRoot && result.hasViteClient) {
    console.log('🎉 Frontend appears to be working correctly!');
  }
  console.log('\n---\n');
  
  // Test backend
  checkEndpoint('http://localhost:8000/api/insights', (err, result) => {
    if (err) {
      console.log('❌ Backend not accessible:', err.message);
      return;
    }
    
    console.log('✅ Backend API:');
    console.log(`   Status: ${result.statusCode}`);
    console.log(`   Content length: ${result.contentLength} bytes`);
    
    if (result.statusCode === 200) {
      console.log('🎉 Backend API is working correctly!');
    }
  });
});
