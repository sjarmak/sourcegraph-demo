import json
import asyncio
import aiohttp
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging
from pathlib import Path
from sqlalchemy.orm import Session
from app.models import Insight
from app.core.text_processor import TextProcessor
from app.schemas import InsightCreate

logger = logging.getLogger(__name__)

class SourceManager:
    """Manages multiple data sources with modular, extensible architecture."""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent / "sources.json"
        
        self.config_path = config_path
        self.text_processor = TextProcessor()
        self.sources_config = self._load_sources_config()
    
    def _load_sources_config(self) -> Dict[str, Any]:
        """Load sources configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading sources config: {e}")
            return {"sources": []}
    
    def get_enabled_sources(self) -> List[Dict[str, Any]]:
        """Get list of enabled sources."""
        return [source for source in self.sources_config.get("sources", []) 
                if source.get("enabled", True)]
    
    def get_source_names(self) -> List[str]:
        """Get list of enabled source names."""
        return [source["name"] for source in self.get_enabled_sources()]
    
    async def scrape_all_sources(
        self, 
        db: Session, 
        hours_back: int = 24,
        sources: Optional[List[str]] = None
    ) -> Dict[str, int]:
        """Scrape all or specific enabled sources."""
        results = {}
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        enabled_sources = self.get_enabled_sources()
        if sources:
            enabled_sources = [s for s in enabled_sources if s["name"] in sources]
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for source_config in enabled_sources:
                task = self._scrape_single_source(
                    session, source_config, cutoff_time
                )
                tasks.append(task)
            
            source_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for source_config, entries in zip(enabled_sources, source_results):
                source_name = source_config["name"]
                if isinstance(entries, Exception):
                    logger.error(f"Error scraping {source_name}: {entries}")
                    results[source_name] = 0
                else:
                    count = await self._process_entries(
                        db, source_name, entries, source_config
                    )
                    results[source_name] = count
        
        return results
    
    async def _scrape_single_source(
        self, 
        session: aiohttp.ClientSession,
        source_config: Dict[str, Any],
        cutoff_time: datetime
    ) -> List[Dict]:
        """Scrape a single source based on its configuration."""
        source_name = source_config["name"]
        endpoint = source_config["endpoint"]
        source_type = source_config.get("type", "rss")
        
        try:
            if source_type == "rss":
                return await self._scrape_rss_source(
                    session, source_config, cutoff_time
                )
            else:
                logger.warning(f"Unsupported source type: {source_type}")
                return []
        except Exception as e:
            logger.error(f"Error scraping {source_name} from {endpoint}: {e}")
            raise
    
    async def _scrape_rss_source(
        self,
        session: aiohttp.ClientSession,
        source_config: Dict[str, Any],
        cutoff_time: datetime
    ) -> List[Dict]:
        """Scrape RSS feed source."""
        endpoint = source_config["endpoint"]
        parser_config = source_config.get("parser_config", {})
        keywords = source_config.get("relevance_keywords", [])
        
        async with session.get(endpoint, timeout=30) as response:
            if response.status == 200:
                content = await response.text()
                feed = feedparser.parse(content)
                
                relevant_entries = []
                for entry in feed.entries:
                    # Parse entry date
                    entry_date = self._parse_entry_date(entry, parser_config)
                    if entry_date and entry_date > cutoff_time:
                        # Filter for relevant content
                        if self._is_relevant_content(entry, keywords):
                            processed_entry = self._extract_entry_data(
                                entry, parser_config
                            )
                            processed_entry['published'] = entry_date
                            relevant_entries.append(processed_entry)
                
                return relevant_entries
        
        return []
    
    def _parse_entry_date(
        self, 
        entry, 
        parser_config: Dict[str, Any]
    ) -> Optional[datetime]:
        """Parse entry date using parser configuration."""
        date_fields = parser_config.get("date_fields", ["published_parsed", "updated_parsed"])
        
        # Try parsed date fields first
        for field in date_fields:
            if hasattr(entry, field) and getattr(entry, field):
                try:
                    time_struct = getattr(entry, field)
                    return datetime(*time_struct[:6])
                except:
                    continue
        
        # Fallback to string parsing
        string_date_fields = ["published", "updated"]
        for field in string_date_fields:
            if hasattr(entry, field) and getattr(entry, field):
                try:
                    date_str = getattr(entry, field)
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except:
                    continue
        
        return None
    
    def _is_relevant_content(
        self, 
        entry, 
        keywords: List[str]
    ) -> bool:
        """Check if entry content is relevant based on keywords."""
        if not keywords:
            return True  # If no keywords specified, accept all
        
        text_to_check = ' '.join([
            entry.get('title', ''),
            entry.get('summary', ''),
            entry.get('content', ''),
            ' '.join([tag.get('term', '') for tag in entry.get('tags', [])])
        ]).lower()
        
        return any(keyword.lower() in text_to_check for keyword in keywords)
    
    def _extract_entry_data(
        self, 
        entry, 
        parser_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract data from entry using parser configuration."""
        data = {}
        
        # Extract title
        title_field = parser_config.get("title_field", "title")
        data['title'] = entry.get(title_field, '')
        
        # Extract content
        content_fields = parser_config.get("content_fields", ["summary", "content"])
        content_parts = []
        for field in content_fields:
            if field == "content" and entry.get('content'):
                # Handle content array format
                content_parts.append(entry.get('content', [{}])[0].get('value', ''))
            else:
                content_parts.append(entry.get(field, ''))
        data['summary'] = '\n'.join(filter(None, content_parts))
        data['content'] = data['summary']  # For compatibility
        
        # Extract link
        link_field = parser_config.get("link_field", "link")
        data['link'] = entry.get(link_field, '')
        
        # Extract author
        author_field = parser_config.get("author_field", "author")
        data['author'] = entry.get(author_field, '')
        
        # Extract tags
        tags_field = parser_config.get("tags_field", "tags")
        if entry.get(tags_field):
            data['tags'] = [tag.get('term', '') for tag in entry.get(tags_field, [])]
        else:
            data['tags'] = []
        
        return data
    
    async def _process_entries(
        self, 
        db: Session, 
        source_name: str, 
        entries: List[Dict],
        source_config: Dict[str, Any]
    ) -> int:
        """Process entries and save as insights."""
        count = 0
        for entry in entries:
            try:
                # Check if we already have this insight
                existing = db.query(Insight).filter(
                    Insight.link == entry['link'],
                    Insight.tool == source_name
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
                
                # Override with source data
                insight_data.tool = source_name
                insight_data.date = entry['published']
                insight_data.link = entry['link']
                
                # Use original title if better
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
                logger.error(f"Error processing entry from {source_name}: {e}")
                continue
        
        if count > 0:
            db.commit()
        
        return count
