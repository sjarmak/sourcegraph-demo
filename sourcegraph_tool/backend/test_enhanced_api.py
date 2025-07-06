#!/usr/bin/env python3
"""
Comprehensive test of the enhanced Agentic Insight Tracker API.
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
    print("🚀 Testing Enhanced Agentic Insight Tracker API")
    print("=" * 60)
    
    # Test health endpoint
    status, data = test_endpoint("/health")
    print(f"✅ Health check: {status} - {data}")
    
    # Test enhanced insights endpoint with new filters
    print("\n📊 Testing enhanced insights filtering...")
    
    # Test matched keywords filter
    status, data = test_endpoint("/api/insights", {"matched_keywords": "claude,copilot", "limit": 2})
    if status == 200:
        print(f"✅ Keyword filter: Found {len(data)} insights with claude/copilot keywords")
        if data:
            example = data[0]
            print(f"   Example: '{example['title'][:50]}...' - Keywords: {example.get('matched_keywords', [])}")
    else:
        print(f"❌ Keyword filter failed: {status}")
    
    # Test source type filter
    status, data = test_endpoint("/api/insights", {"source_type": "rss", "limit": 3})
    if status == 200:
        print(f"✅ Source type filter: Found {len(data)} RSS insights")
    else:
        print(f"❌ Source type filter failed: {status}")
    
    # Test new endpoints
    print("\n🔍 Testing new metadata endpoints...")
    
    # Test keywords endpoint
    status, keywords = test_endpoint("/api/insights/keywords")
    if status == 200:
        print(f"✅ Keywords endpoint: {len(keywords)} unique keywords")
        print(f"   Sample keywords: {keywords[:5]}")
    else:
        print(f"❌ Keywords endpoint failed: {status}")
    
    # Test source types endpoint
    status, source_types = test_endpoint("/api/insights/source-types")
    if status == 200:
        print(f"✅ Source types endpoint: {source_types}")
    else:
        print(f"❌ Source types endpoint failed: {status}")
    
    # Test sources endpoint (existing)
    status, sources = test_endpoint("/api/insights/sources")
    if status == 200:
        print(f"✅ Sources endpoint: {len(sources)} configured sources")
        print(f"   New sources added: {[s for s in sources if 'reddit' in s or 'dev_to' in s or 'arxiv' in s or 'medium' in s]}")
    else:
        print(f"❌ Sources endpoint failed: {status}")
    
    # Test combined filtering
    print("\n🎯 Testing advanced filtering combinations...")
    
    status, data = test_endpoint("/api/insights", {
        "matched_keywords": "ai",
        "source_type": "rss",
        "from_hours": 24,
        "limit": 3
    })
    if status == 200:
        print(f"✅ Combined filtering: Found {len(data)} recent AI insights from RSS sources")
        for i, insight in enumerate(data[:2]):
            print(f"   {i+1}. {insight['tool']}: '{insight['title'][:40]}...'")
            print(f"      Keywords: {insight.get('matched_keywords', [])}")
    else:
        print(f"❌ Combined filtering failed: {status}")
    
    print("\n" + "=" * 60)
    print("✅ Enhanced API testing completed!")

if __name__ == "__main__":
    main()
