#!/usr/bin/env python3
"""
RSS Feed Testing Script
Tests all RSS feeds from sources.json file to check their availability and parsability.
"""

import json
import requests
import feedparser
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import os
import sys

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def load_sources(sources_path: str) -> List[Dict[str, Any]]:
    """Load RSS sources from sources.json file."""
    try:
        with open(sources_path, 'r') as f:
            data = json.load(f)
        return data.get('sources', [])
    except FileNotFoundError:
        print(f"Error: Sources file not found at {sources_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in sources file: {e}")
        return []

def test_rss_feed(source: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
    """Test a single RSS feed and return results."""
    name = source.get('name', 'Unknown')
    endpoint = source.get('endpoint', '')
    enabled = source.get('enabled', False)
    
    result = {
        'name': name,
        'endpoint': endpoint,
        'enabled': enabled,
        'status_code': None,
        'response_time': None,
        'can_parse': False,
        'entry_count': 0,
        'error': None,
        'feed_title': None,
        'last_updated': None
    }
    
    if not enabled:
        result['error'] = 'Feed disabled in config'
        return result
    
    if not endpoint:
        result['error'] = 'No endpoint specified'
        return result
    
    print(f"Testing {name}: {endpoint}")
    
    try:
        # Make HTTP request with timeout
        start_time = time.time()
        response = requests.get(endpoint, timeout=timeout, headers={
            'User-Agent': 'Mozilla/5.0 (RSS Feed Tester)'
        })
        response_time = time.time() - start_time
        
        result['status_code'] = response.status_code
        result['response_time'] = round(response_time, 2)
        
        if response.status_code != 200:
            result['error'] = f'HTTP {response.status_code}: {response.reason}'
            return result
        
        # Try to parse with feedparser
        try:
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                result['error'] = f'Feed parse error: {feed.bozo_exception}'
                # Continue even if bozo, as many feeds still work
            
            result['can_parse'] = True
            result['entry_count'] = len(feed.entries)
            
            # Extract feed metadata
            if hasattr(feed, 'feed'):
                result['feed_title'] = feed.feed.get('title', 'No title')
                if hasattr(feed.feed, 'updated_parsed') and feed.feed.updated_parsed:
                    result['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S', 
                                                         feed.feed.updated_parsed)
            
            # Check if we actually got entries
            if result['entry_count'] == 0:
                result['error'] = 'No entries found in feed'
                
        except Exception as parse_error:
            result['can_parse'] = False
            result['error'] = f'Parse error: {str(parse_error)}'
            
    except requests.exceptions.Timeout:
        result['error'] = f'Request timeout after {timeout} seconds'
    except requests.exceptions.ConnectionError as e:
        result['error'] = f'Connection error: {str(e)}'
    except requests.exceptions.RequestException as e:
        result['error'] = f'Request error: {str(e)}'
    except Exception as e:
        result['error'] = f'Unexpected error: {str(e)}'
    
    return result

def generate_report(results: List[Dict[str, Any]]) -> str:
    """Generate a summary report of RSS feed test results."""
    total_feeds = len(results)
    enabled_feeds = len([r for r in results if r['enabled']])
    working_feeds = len([r for r in results if r['can_parse'] and r['entry_count'] > 0])
    failed_feeds = enabled_feeds - working_feeds
    
    report = f"""
RSS Feed Testing Report
=======================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Summary:
- Total feeds configured: {total_feeds}
- Enabled feeds: {enabled_feeds}
- Working feeds: {working_feeds}
- Failed feeds: {failed_feeds}
- Success rate: {(working_feeds/enabled_feeds*100):.1f}% (of enabled feeds)

Detailed Results:
"""
    
    # Sort results by status (working first, then failed)
    sorted_results = sorted(results, key=lambda x: (
        not x['enabled'],  # Disabled feeds last
        not x['can_parse'],  # Working feeds first
        x['entry_count'] == 0,  # Feeds with entries first
        x['name']  # Then alphabetical
    ))
    
    for result in sorted_results:
        status = "✅ WORKING" if result['can_parse'] and result['entry_count'] > 0 else "❌ FAILED"
        if not result['enabled']:
            status = "⚪ DISABLED"
        
        report += f"\n{status} {result['name']}\n"
        report += f"  URL: {result['endpoint']}\n"
        
        if result['status_code']:
            report += f"  HTTP Status: {result['status_code']}\n"
        if result['response_time']:
            report += f"  Response Time: {result['response_time']}s\n"
        if result['can_parse']:
            report += f"  Entries: {result['entry_count']}\n"
        if result['feed_title']:
            report += f"  Feed Title: {result['feed_title']}\n"
        if result['last_updated']:
            report += f"  Last Updated: {result['last_updated']}\n"
        if result['error']:
            report += f"  Error: {result['error']}\n"
    
    return report

def main():
    """Main function to run RSS feed tests."""
    print("RSS Feed Testing Script")
    print("=" * 50)
    
    # Path to sources.json file
    sources_path = Path(__file__).parent / 'app' / 'core' / 'sources.json'
    
    # Load sources
    sources = load_sources(sources_path)
    if not sources:
        print("No sources found to test.")
        return
    
    print(f"Found {len(sources)} RSS sources to test")
    print("-" * 50)
    
    # Test each feed
    results = []
    for i, source in enumerate(sources, 1):
        print(f"[{i}/{len(sources)}] ", end="")
        result = test_rss_feed(source)
        results.append(result)
        
        # Brief status update
        if result['can_parse'] and result['entry_count'] > 0:
            print(f"✅ OK ({result['entry_count']} entries)")
        elif not result['enabled']:
            print("⚪ DISABLED")
        else:
            print(f"❌ FAILED: {result['error']}")
        
        # Small delay to be respectful to servers
        time.sleep(0.5)
    
    # Generate and save report
    report = generate_report(results)
    
    # Save report to file
    report_path = Path(__file__).parent / 'rss_feed_test_report.txt'
    with open(report_path, 'w') as f:
        f.write(report)
    
    print("\n" + "=" * 50)
    print(f"Report saved to: {report_path}")
    print(report)

if __name__ == "__main__":
    main()
