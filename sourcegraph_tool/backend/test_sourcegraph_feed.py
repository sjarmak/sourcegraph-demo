#!/usr/bin/env python3
"""
Test script to specifically check the Sourcegraph feed and debugging.
"""

import asyncio
import aiohttp
import feedparser
import json
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.source_manager import SourceManager
from app.core.keyword_filter import KeywordFilter
from app.core.tool_detector import ToolDetector


async def test_sourcegraph_feed():
    """Test the Sourcegraph feed specifically."""
    
    print("=== Testing Sourcegraph Feed ===")
    
    # Test 1: Direct HTTP request with User-Agent
    print("\n1. Testing direct HTTP request...")
    
    headers = {
        'User-Agent': 'AITrackerBot/1.0 (Agentic Insight Tracker; +https://github.com/your-org/ai-tracker)',
        'Accept': 'application/rss+xml, application/xml, text/xml, */*',
        'Accept-Encoding': 'gzip, deflate'
    }
    
    url = "https://about.sourcegraph.com/blog/rss.xml"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                print(f"Status: {response.status}")
                print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
                
                if response.status == 200:
                    content = await response.text()
                    print(f"Content length: {len(content)} characters")
                    
                    # Test 2: Parse with feedparser
                    print("\n2. Testing feedparser...")
                    feed = feedparser.parse(content)
                    
                    print(f"Feed title: {feed.feed.get('title', 'Unknown')}")
                    print(f"Feed bozo: {feed.bozo}")
                    if hasattr(feed, 'bozo_exception') and feed.bozo_exception:
                        print(f"Bozo exception: {feed.bozo_exception}")
                    
                    print(f"Number of entries: {len(feed.entries)}")
                    
                    if feed.entries:
                        # Show first entry
                        entry = feed.entries[0]
                        print(f"\nFirst entry:")
                        print(f"  Title: {entry.get('title', 'No title')}")
                        print(f"  Published: {entry.get('published', 'No date')}")
                        print(f"  Link: {entry.get('link', 'No link')}")
                        print(f"  Summary: {entry.get('summary', 'No summary')[:200]}...")
                    
                    # Test 3: Keyword matching
                    print("\n3. Testing keyword matching...")
                    
                    # Initialize keyword filter
                    keyword_filter = KeywordFilter.from_config_file()
                    
                    # Load sources config to add relevance keywords
                    sources_config_path = Path(__file__).parent / "app" / "core" / "sources.json"
                    with open(sources_config_path, 'r') as f:
                        sources_config = json.load(f)
                    
                    # Find sourcegraph source config
                    sourcegraph_config = None
                    for source_config in sources_config.get("sources", []):
                        if source_config["name"] == "sourcegraph":
                            sourcegraph_config = source_config
                            break
                    
                    if sourcegraph_config:
                        relevance_keywords = sourcegraph_config.get("relevance_keywords", [])
                        keyword_filter.add_source_keywords("sourcegraph", relevance_keywords)
                        print(f"Added {len(relevance_keywords)} relevance keywords for sourcegraph")
                        
                        # Show effective keywords
                        effective_keywords = keyword_filter.get_keywords_for_source("sourcegraph")
                        print(f"Total effective keywords: {len(effective_keywords)}")
                        print(f"Keywords: {sorted(list(effective_keywords))[:10]}...")  # Show first 10
                        
                        # Test keyword matching on first few entries
                        if feed.entries:
                            print(f"\nTesting keyword matching on first 3 entries...")
                            for i, entry in enumerate(feed.entries[:3]):
                                title = entry.get('title', '')
                                summary = entry.get('summary', '')
                                content = ""
                                if entry.get('content'):
                                    if isinstance(entry.content, list) and entry.content:
                                        content = entry.content[0].get('value', '')
                                    else:
                                        content = str(entry.content)
                                
                                text_for_filtering = f"{title} {summary} {content}"
                                matched_keywords = keyword_filter.match("sourcegraph", text_for_filtering)
                                print(f"Entry {i+1}: '{title[:60]}...'")
                                print(f"  Matched keywords: {matched_keywords}")
                                
                                if matched_keywords:
                                    # Test tool detection
                                    tool_detector = ToolDetector()
                                    mentioned_tools = tool_detector.detect_tools(matched_keywords)
                                    mentioned_concepts = tool_detector.detect_concepts(matched_keywords)
                                    print(f"  Detected tools: {mentioned_tools}")
                                    print(f"  Detected concepts: {mentioned_concepts}")
                                    break  # Found a match, no need to continue
                            
                            # If no matches found, let's see what keywords we're looking for
                            if not any(keyword_filter.match("sourcegraph", f"{e.get('title', '')} {e.get('summary', '')}") for e in feed.entries[:3]):
                                print(f"\nNo matches found in first 3 entries.")
                                print(f"Sample keywords we're looking for: {list(effective_keywords)[:20]}")
                                
                                # Check if 'sourcegraph' keyword itself appears
                                for i, entry in enumerate(feed.entries[:3]):
                                    text = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
                                    if 'sourcegraph' in text:
                                        print(f"Entry {i+1} contains 'sourcegraph' in text")
                                    if 'cody' in text:
                                        print(f"Entry {i+1} contains 'cody' in text")
                                    if 'code search' in text:
                                        print(f"Entry {i+1} contains 'code search' in text")
                    
                else:
                    print(f"HTTP Error: {response.status}")
                    
        except Exception as e:
            print(f"Request failed: {e}")
    
    # Test 4: Full source manager test
    print("\n5. Testing with SourceManager...")
    
    try:
        source_manager = SourceManager()
        
        # Get source info
        source_info = source_manager.get_source_info()
        print(f"Total sources: {source_info['total_sources']}")
        print(f"Enabled sources: {source_info['enabled_sources']}")
        
        # Find sourcegraph source
        sourcegraph_source_info = None
        for source in source_info['sources']:
            if source['name'] == 'sourcegraph':
                sourcegraph_source_info = source
                break
        
        if sourcegraph_source_info:
            print(f"Sourcegraph source info: {sourcegraph_source_info}")
        else:
            print("Sourcegraph source not found in enabled sources!")
    
    except Exception as e:
        print(f"SourceManager test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_sourcegraph_feed())
