#!/usr/bin/env python3
"""
Test script for the enhanced ingestion system with keyword filtering.
"""
import sys
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.core.keyword_filter import KeywordFilter
from app.core.sources import RssSource, ArxivSource

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_keyword_filter():
    """Test the KeywordFilter functionality."""
    print("=" * 50)
    print("Testing KeywordFilter")
    print("=" * 50)
    
    # Create keyword filter with test data
    global_keywords = ["ai", "coding", "assistant", "sourcegraph", "copilot"]
    per_source_keywords = {
        "test_source": ["python", "javascript", "development"]
    }
    
    keyword_filter = KeywordFilter(global_keywords, per_source_keywords)
    
    # Test cases
    test_cases = [
        ("AI coding assistant helps developers", "test_source", ["ai", "coding", "assistant"]),
        ("Python development with Sourcegraph", "test_source", ["python", "sourcegraph"]),
        ("Random blog post about cooking", "test_source", []),
        ("GitHub Copilot integration", "other_source", ["copilot"]),
    ]
    
    for text, source, expected_keywords in test_cases:
        matched = keyword_filter.match(source, text)
        matched_set = set(matched)
        expected_set = set(expected_keywords)
        
        print(f"Text: '{text[:50]}...'")
        print(f"Source: {source}")
        print(f"Expected: {expected_set}")
        print(f"Matched: {matched_set}")
        print(f"✅ PASS" if matched_set >= expected_set else f"❌ FAIL")
        print("-" * 30)


async def test_rss_source():
    """Test RSS source with keyword filtering."""
    print("=" * 50)
    print("Testing RSS Source with Keyword Filtering")
    print("=" * 50)
    
    # Create keyword filter
    keyword_filter = KeywordFilter.from_config_file()
    
    # Test RSS source configuration
    source_config = {
        "name": "test_hackernews",
        "type": "rss",
        "endpoint": "https://hnrss.org/newest?q=AI+agent+OR+coding+assistant",
        "parser_config": {
            "title_field": "title",
            "content_fields": ["summary", "content"],
            "date_fields": ["published_parsed", "updated_parsed"],
            "link_field": "link",
            "author_field": "author",
            "tags_field": "tags"
        },
        "enabled": True
    }
    
    # Create RSS source handler
    rss_source = RssSource(source_config, keyword_filter)
    
    print(f"RSS Source Info: {rss_source.get_source_info()}")
    
    try:
        import aiohttp
        
        # Test fetching (limit to last 1 hour to avoid too many results)
        cutoff_time = datetime.now() - timedelta(hours=1)
        
        async with aiohttp.ClientSession() as session:
            entries = await rss_source.fetch(session, cutoff_time)
            
        print(f"Found {len(entries)} entries from RSS feed")
        
        # Show first few entries
        for i, entry in enumerate(entries[:3]):
            print(f"\nEntry {i+1}:")
            print(f"  Title: {entry.get('title', 'N/A')[:80]}...")
            print(f"  Link: {entry.get('link', 'N/A')}")
            print(f"  Matched Keywords: {entry.get('matched_keywords', [])}")
            print(f"  Published: {entry.get('published', 'N/A')}")
            
    except Exception as e:
        print(f"RSS test failed: {e}")


async def test_arxiv_source():
    """Test arXiv source with keyword filtering."""
    print("=" * 50)
    print("Testing arXiv Source with Keyword Filtering")
    print("=" * 50)
    
    # Create keyword filter
    keyword_filter = KeywordFilter.from_config_file()
    
    # Test arXiv source configuration
    source_config = {
        "name": "test_arxiv",
        "type": "arxiv",
        "endpoint": "http://export.arxiv.org/api/query",
        "search_terms": ["code assistant", "AI code generation"],
        "categories": ["cs.AI", "cs.SE"],
        "max_results": 10,
        "sort_by": "submittedDate",
        "sort_order": "descending",
        "enabled": True
    }
    
    # Create arXiv source handler
    arxiv_source = ArxivSource(source_config, keyword_filter)
    
    print(f"arXiv Source Info: {arxiv_source.get_source_info()}")
    
    try:
        import aiohttp
        
        # Test fetching (limit to last 7 days)
        cutoff_time = datetime.now() - timedelta(days=7)
        
        async with aiohttp.ClientSession() as session:
            entries = await arxiv_source.fetch(session, cutoff_time)
            
        print(f"Found {len(entries)} papers from arXiv")
        
        # Show first few entries
        for i, entry in enumerate(entries[:2]):
            print(f"\nPaper {i+1}:")
            print(f"  Title: {entry.get('title', 'N/A')[:80]}...")
            print(f"  Link: {entry.get('link', 'N/A')}")
            print(f"  Matched Keywords: {entry.get('matched_keywords', [])}")
            print(f"  Authors: {entry.get('author', 'N/A')[:50]}...")
            print(f"  Published: {entry.get('published', 'N/A')}")
            
    except Exception as e:
        print(f"arXiv test failed: {e}")


async def main():
    """Run all tests."""
    print("🚀 Testing Enhanced Ingestion System")
    print("=" * 60)
    
    try:
        await test_keyword_filter()
        await test_rss_source()
        await test_arxiv_source()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
