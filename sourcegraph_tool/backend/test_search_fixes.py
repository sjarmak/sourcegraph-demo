#!/usr/bin/env python3
"""
Test the search and pagination fixes for the Agentic Insight Tracker.
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(endpoint, params=None):
    """Test an API endpoint and return the response."""
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.get(url, params=params)
        return response.status_code, response.json()
    except Exception as e:
        return None, str(e)

def main():
    print("🔍 Testing Search and Pagination Fixes")
    print("=" * 60)
    
    # Test 1: Default behavior should show all records from last 30 days
    print("\n1️⃣ Testing default insights retrieval...")
    status, data = test_endpoint("/api/insights")
    if status == 200:
        print(f"✅ Default query: Found {len(data)} insights (should be >50)")
        
        # Show source distribution
        from collections import Counter
        sources = Counter([insight['tool'] for insight in data])
        print(f"   Top sources: {dict(list(sources.most_common(5)))}")
        
        # Show date range
        if data:
            dates = [insight['date'][:10] for insight in data]
            print(f"   Date range: {min(dates)} to {max(dates)}")
    else:
        print(f"❌ Default query failed: {status}")
    
    # Test 2: Search for 'sourcegraph' should find results
    print("\n2️⃣ Testing search for 'sourcegraph'...")
    status, data = test_endpoint("/api/insights", {"q": "sourcegraph"})
    if status == 200:
        print(f"✅ Sourcegraph search: Found {len(data)} insights")
        for i, insight in enumerate(data[:2]):
            print(f"   {i+1}. {insight['tool']}: \"{insight['title'][:50]}...\"")
            print(f"      Keywords: {insight.get('matched_keywords', [])}")
    else:
        print(f"❌ Sourcegraph search failed: {status}")
    
    # Test 3: Search for 'cody' should find results
    print("\n3️⃣ Testing search for 'cody'...")
    status, data = test_endpoint("/api/insights", {"q": "cody"})
    if status == 200:
        print(f"✅ Cody search: Found {len(data)} insights")
        for i, insight in enumerate(data[:2]):
            print(f"   {i+1}. {insight['tool']}: \"{insight['title'][:50]}...\"")
            if 'cody' in insight['title'].lower():
                print("      ✅ Found 'cody' in title")
            if insight.get('matched_keywords') and any('cody' in kw.lower() for kw in insight['matched_keywords']):
                print("      ✅ Found 'cody' in matched keywords")
    else:
        print(f"❌ Cody search failed: {status}")
    
    # Test 4: Search for 'claude' should find results
    print("\n4️⃣ Testing search for 'claude'...")
    status, data = test_endpoint("/api/insights", {"q": "claude"})
    if status == 200:
        print(f"✅ Claude search: Found {len(data)} insights")
        for i, insight in enumerate(data[:2]):
            print(f"   {i+1}. {insight['tool']}: \"{insight['title'][:50]}...\"")
            print(f"      Keywords: {insight.get('matched_keywords', [])}")
    else:
        print(f"❌ Claude search failed: {status}")
    
    # Test 5: Search should work across all fields (title, summary, tool, etc.)
    print("\n5️⃣ Testing enhanced field search...")
    status, data = test_endpoint("/api/insights", {"q": "hackernews"})
    if status == 200:
        print(f"✅ Tool name search: Found {len(data)} insights with 'hackernews'")
        hackernews_tools = [insight for insight in data if 'hackernews' in insight['tool'].lower()]
        print(f"   {len(hackernews_tools)} results from tool name matching")
    else:
        print(f"❌ Tool name search failed: {status}")
    
    # Test 6: Test limit behavior
    print("\n6️⃣ Testing explicit limit...")
    status, data = test_endpoint("/api/insights", {"limit": 10})
    if status == 200:
        print(f"✅ Explicit limit: Found {len(data)} insights (should be 10)")
    else:
        print(f"❌ Explicit limit failed: {status}")
    
    # Test 7: Test search with matched keywords filter
    print("\n7️⃣ Testing matched keywords filter...")
    status, data = test_endpoint("/api/insights", {"matched_keywords": "claude,cody"})
    if status == 200:
        print(f"✅ Matched keywords filter: Found {len(data)} insights")
        for insight in data[:2]:
            keywords = insight.get('matched_keywords', [])
            has_claude = any('claude' in kw.lower() for kw in keywords)
            has_cody = any('cody' in kw.lower() for kw in keywords)
            print(f"   Keywords: {keywords} (Claude: {has_claude}, Cody: {has_cody})")
    else:
        print(f"❌ Matched keywords filter failed: {status}")
    
    print("\n" + "=" * 60)
    print("✅ Search and pagination testing completed!")

if __name__ == "__main__":
    main()
