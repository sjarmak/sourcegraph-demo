import asyncio
import aiohttp
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from sqlalchemy.orm import Session
from app.models import Insight
from app.core.text_processor import TextProcessor
from app.schemas import InsightCreate

logger = logging.getLogger(__name__)

class RSSFeedScraper:
    """Scrapes RSS feeds for coding agent and dev productivity insights."""
    
    def __init__(self):
        self.text_processor = TextProcessor()
        self.feeds = {
            # AI/ML Agent feeds
            "anthropic": "https://www.anthropic.com/news/rss.xml",
            "openai": "https://openai.com/blog/rss.xml",
            "sourcegraph": "https://about.sourcegraph.com/blog/rss.xml",
            "github": "https://github.blog/feed/",
            
            # Dev productivity feeds
            "dev.to": "https://dev.to/feed/tag/productivity",
            "hackernews": "https://hnrss.org/newest?q=AI+agent+OR+coding+assistant",
            "reddit_programming": "https://www.reddit.com/r/programming/.rss",
            "stackoverflow": "https://stackoverflow.com/feeds/tag?tagnames=artificial-intelligence&sort=newest",
            
            # Tech company blogs
            "aws": "https://aws.amazon.com/blogs/aws/feed/",
            "google": "https://blog.google/technology/developers/rss/",
            "microsoft": "https://devblogs.microsoft.com/feed/",
            "meta": "https://engineering.fb.com/feed/",
            "netflix": "https://netflixtechblog.com/feed",
            "uber": "https://eng.uber.com/rss/",
            "airbnb": "https://medium.com/airbnb-engineering/feed",
        }
    
    async def scrape_all_feeds(self, db: Session, hours_back: int = 24) -> Dict[str, int]:
        """Scrape all configured RSS feeds and return count of new insights per feed."""
        results = {}
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for feed_name, feed_url in self.feeds.items():
                task = self._scrape_single_feed(session, feed_name, feed_url, cutoff_time)
                tasks.append(task)
            
            feed_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for feed_name, entries in zip(self.feeds.keys(), feed_results):
                if isinstance(entries, Exception):
                    logger.error(f"Error scraping {feed_name}: {entries}")
                    results[feed_name] = 0
                else:
                    count = await self._process_entries(db, feed_name, entries)
                    results[feed_name] = count
        
        return results
    
    async def _scrape_single_feed(self, session: aiohttp.ClientSession, 
                                 feed_name: str, feed_url: str, 
                                 cutoff_time: datetime) -> List[Dict]:
        """Scrape a single RSS feed."""
        try:
            async with session.get(feed_url, timeout=30) as response:
                if response.status == 200:
                    content = await response.text()
                    feed = feedparser.parse(content)
                    
                    relevant_entries = []
                    for entry in feed.entries:
                        # Parse entry date
                        entry_date = self._parse_entry_date(entry)
                        if entry_date and entry_date > cutoff_time:
                            # Filter for AI/agent/productivity related content
                            if self._is_relevant_content(entry):
                                # Handle link extraction with fallback to canonical/alternate links
                                link = entry.get('link', '')
                                if not link and 'links' in entry and entry.get('links'):
                                    # Prefer canonical or alternate links for AMP pages
                                    for link_obj in entry.links:
                                        if hasattr(link_obj, 'get'):
                                            rel = link_obj.get('rel')
                                            if rel in ('alternate', 'canonical'):
                                                link = link_obj.get('href', '')
                                                break
                                        elif hasattr(link_obj, 'href'):
                                            link = link_obj.href
                                            break
                                
                                relevant_entries.append({
                                    'title': entry.get('title', ''),
                                    'summary': entry.get('summary', ''),
                                    'content': entry.get('content', [{}])[0].get('value', '') if entry.get('content') else '',
                                    'link': link,
                                    'published': entry_date,
                                    'author': entry.get('author', ''),
                                    'tags': [tag.get('term', '') for tag in entry.get('tags', [])]
                                })
                    
                    return relevant_entries
        except Exception as e:
            logger.error(f"Error fetching {feed_name} from {feed_url}: {e}")
            raise
        
        return []
    
    def _parse_entry_date(self, entry) -> Optional[datetime]:
        """Parse entry date from various RSS date formats."""
        date_fields = ['published_parsed', 'updated_parsed']
        for field in date_fields:
            if hasattr(entry, field) and getattr(entry, field):
                try:
                    time_struct = getattr(entry, field)
                    return datetime(*time_struct[:6])
                except:
                    continue
        
        # Fallback to string parsing
        date_strings = ['published', 'updated']
        for field in date_strings:
            if hasattr(entry, field) and getattr(entry, field):
                try:
                    return datetime.fromisoformat(getattr(entry, field).replace('Z', '+00:00'))
                except:
                    continue
        
        return None
    
    def _is_relevant_content(self, entry) -> bool:
        """Check if entry content is relevant to coding agents/dev productivity."""
        keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'agent', 'assistant',
            'coding', 'development', 'developer', 'programming', 'productivity',
            'automation', 'tool', 'devops', 'ci/cd', 'testing', 'deployment',
            'copilot', 'claude', 'gpt', 'llm', 'code generation', 'refactoring',
            'debugging', 'ide', 'editor', 'workflow', 'efficiency'
        ]
        
        text_to_check = ' '.join([
            entry.get('title', ''),
            entry.get('summary', ''),
            entry.get('content', ''),
            ' '.join(entry.get('tags', []))
        ]).lower()
        
        return any(keyword in text_to_check for keyword in keywords)
    
    async def _process_entries(self, db: Session, feed_name: str, entries: List[Dict]) -> int:
        """Process entries and save as insights."""
        count = 0
        for entry in entries:
            try:
                # Check if we already have this insight
                existing = db.query(Insight).filter(
                    Insight.link == entry['link'],
                    Insight.tool == feed_name
                ).first()
                
                if existing:
                    continue
                
                # Create raw text for processing
                raw_text = f"Title: {entry['title']}\n"
                raw_text += f"Summary: {entry['summary']}\n"
                raw_text += f"Content: {entry['content']}\n"
                raw_text += f"Tags: {', '.join(entry['tags'])}\n"
                raw_text += f"Link: {entry['link']}"
                
                # Process with text processor
                insight_data = self.text_processor.extract_insight(raw_text)
                
                # Override tool and date with RSS feed data
                insight_data.tool = feed_name
                insight_data.date = entry['published']
                insight_data.link = entry['link']
                
                # Use original title if it's better
                if len(entry['title']) > 10:
                    insight_data.title = entry['title'][:200]
                
                # Create database record
                db_insight = Insight(
                    tool=insight_data.tool,
                    date=insight_data.date,
                    title=insight_data.title,
                    summary=insight_data.summary,
                    topics=insight_data.topics,
                    link=insight_data.link
                )
                
                db.add(db_insight)
                count += 1
                
            except Exception as e:
                logger.error(f"Error processing entry from {feed_name}: {e}")
                continue
        
        if count > 0:
            db.commit()
        
        return count
