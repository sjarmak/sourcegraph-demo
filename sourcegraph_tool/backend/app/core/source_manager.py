import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging
from pathlib import Path
from sqlalchemy.orm import Session
from app.models import Insight
from app.core.text_processor import TextProcessor
from app.core.keyword_filter import KeywordFilter
from app.core.sources import BaseSource, RssSource, ArxivSource
from app.schemas import InsightCreate

logger = logging.getLogger(__name__)

class SourceManager:
    """Manages multiple data sources with modular, extensible architecture."""
    
    def __init__(self, config_path: str = None, keyword_config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent / "sources.json"
        
        self.config_path = config_path
        self.text_processor = TextProcessor()
        self.sources_config = self._load_sources_config()
        
        # Initialize keyword filter
        self.keyword_filter = KeywordFilter.from_config_file(keyword_config_path)
        
        # Override with global keywords from sources.json if available
        global_keywords = self.sources_config.get("global_keywords", [])
        if global_keywords:
            self.keyword_filter.add_global_keywords(global_keywords)
        
        # Source handler registry
        self.source_registry = {
            "rss": RssSource,
            "arxiv": ArxivSource,
        }
    
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
        """Scrape all or specific enabled sources using async semaphore for concurrency control."""
        results = {}
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        enabled_sources = self.get_enabled_sources()
        if sources:
            enabled_sources = [s for s in enabled_sources if s["name"] in sources]
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(10)  # Max 10 concurrent requests
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for source_config in enabled_sources:
                task = self._scrape_source_with_semaphore(
                    semaphore, session, source_config, cutoff_time
                )
                tasks.append(task)
            
            source_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for source_config, entries in zip(enabled_sources, source_results):
                source_name = source_config["name"]
                if isinstance(entries, Exception):
                    logger.error(f"Error scraping {source_name}: {entries}")
                    results[source_name] = 0
                else:
                    count = self._process_entries(db, source_name, entries, source_config)
                    results[source_name] = count
        
        return results
    
    async def _scrape_source_with_semaphore(
        self,
        semaphore: asyncio.Semaphore,
        session: aiohttp.ClientSession,
        source_config: Dict[str, Any],
        cutoff_time: datetime
    ) -> List[Dict]:
        """Scrape a single source with semaphore-controlled concurrency."""
        async with semaphore:
            return await self._scrape_single_source(session, source_config, cutoff_time)
    
    async def _scrape_single_source(
        self, 
        session: aiohttp.ClientSession,
        source_config: Dict[str, Any],
        cutoff_time: datetime
    ) -> List[Dict]:
        """Scrape a single source using appropriate source handler."""
        source_name = source_config["name"]
        source_type = source_config.get("type", "rss")
        
        try:
            # Get the appropriate source handler
            handler_class = self.source_registry.get(source_type)
            if not handler_class:
                logger.warning(f"Unsupported source type: {source_type}")
                return []
            
            # Create handler instance
            handler = handler_class(source_config, self.keyword_filter)
            
            # Fetch entries using the handler
            return await handler.fetch(session, cutoff_time)
            
        except Exception as e:
            logger.error(f"Error scraping {source_name}: {e}")
            raise
    
    def get_source_info(self) -> Dict[str, Any]:
        """Get information about configured sources."""
        sources_info = []
        for source_config in self.get_enabled_sources():
            handler_class = self.source_registry.get(source_config.get("type", "rss"))
            if handler_class:
                handler = handler_class(source_config, self.keyword_filter)
                sources_info.append(handler.get_source_info())
        
        return {
            "total_sources": len(sources_info),
            "enabled_sources": len([s for s in sources_info if s.get("enabled", True)]),
            "sources": sources_info,
            "keyword_filter_info": {
                "total_keywords": len(self.keyword_filter.get_all_keywords()),
                "global_keywords": len(self.keyword_filter.global_keywords)
            }
        }
    
    def _process_entries(
        self, 
        db: Session, 
        source_name: str, 
        entries: List[Dict],
        source_config: Dict[str, Any]
    ) -> int:
        """Process entries and save as insights with matched keywords tracking."""
        count = 0
        for entry in entries:
            try:
                # Check if we already have this insight (using unique constraint)
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
                raw_text += f"Tags: {', '.join(entry.get('tags', []))}\n"
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
                
                # Generate relevant snippet for highlighting
                content_for_snippet = entry.get('content') or entry.get('summary', '')
                snippet = self.text_processor.extract_relevant_snippet(content_for_snippet)
                
                # Create database record with new fields
                db_insight = Insight(
                    tool=insight_data.tool,
                    date=insight_data.date,
                    title=insight_data.title,
                    summary=insight_data.summary,
                    topics=insight_data.topics,
                    link=insight_data.link,
                    snippet=snippet,
                    matched_keywords=entry.get('matched_keywords', []),
                    source_type=source_config.get('type', 'unknown')
                )
                
                db.add(db_insight)
                count += 1
                
            except Exception as e:
                logger.error(f"Error processing entry from {source_name}: {e}")
                continue
        
        if count > 0:
            db.commit()
        
        return count
