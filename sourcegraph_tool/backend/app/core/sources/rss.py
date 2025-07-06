"""
RSS source handler for the Agentic Insight Tracker.
"""
import feedparser
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import aiohttp

from .base import BaseSource

logger = logging.getLogger(__name__)


class RssSource(BaseSource):
    """
    RSS/Atom feed source handler.
    
    Handles standard RSS and Atom feeds with flexible parsing configuration.
    """
    
    async def fetch(
        self, 
        session: aiohttp.ClientSession, 
        cutoff_time: datetime
    ) -> List[Dict[str, Any]]:
        """
        Fetch and process RSS feed entries.
        
        Args:
            session: HTTP session for making requests
            cutoff_time: Only return entries newer than this time
            
        Returns:
            List of processed entries that match keywords and are recent
        """
        endpoint = self.config["endpoint"]
        parser_config = self.config.get("parser_config", {})
        
        try:
            # Fetch RSS feed content
            content = await self._make_request(session, endpoint)
            
            # Parse feed
            feed = feedparser.parse(content)
            
            if feed.bozo and feed.bozo_exception:
                logger.warning(f"Feed parsing warning for {self.name}: {feed.bozo_exception}")
            
            if not feed.entries:
                logger.warning(f"No entries found in feed for {self.name}")
                return []
            
            processed_entries = []
            
            for entry in feed.entries:
                try:
                    # Parse entry date
                    entry_date = self._parse_entry_date(entry, parser_config)
                    if not entry_date:
                        continue
                    
                    # Check if entry is recent enough
                    if not self._is_entry_recent(entry_date, cutoff_time):
                        continue
                    
                    # Extract entry data
                    processed_entry = self._extract_entry_data(entry, parser_config)
                    processed_entry['published'] = entry_date
                    
                    # Apply keyword filtering
                    filtered_entry = self._apply_keyword_filter(processed_entry)
                    if filtered_entry:
                        processed_entries.append(filtered_entry)
                
                except Exception as e:
                    logger.error(f"Error processing entry from {self.name}: {e}")
                    continue
            
            logger.info(f"Found {len(processed_entries)} relevant entries from {self.name}")
            return processed_entries
            
        except Exception as e:
            logger.error(f"Error fetching RSS feed {self.name}: {e}")
            return []
    
    def _parse_entry_date(
        self, 
        entry, 
        parser_config: Dict[str, Any]
    ) -> Optional[datetime]:
        """
        Parse entry date using parser configuration with robust handling.
        
        Args:
            entry: Feed entry object
            parser_config: Parser configuration
            
        Returns:
            Parsed datetime or None if parsing fails
        """
        date_fields = parser_config.get("date_fields", ["published_parsed", "updated_parsed"])
        
        # Try parsed date fields first (most reliable)
        for field in date_fields:
            if hasattr(entry, field) and getattr(entry, field):
                try:
                    time_struct = getattr(entry, field)
                    if time_struct and len(time_struct) >= 6:
                        return datetime(*time_struct[:6])
                except Exception as e:
                    logger.debug(f"Failed to parse {field}: {e}")
                    continue
        
        # Fallback to string parsing
        string_date_fields = ["published", "updated"]
        for field in string_date_fields:
            if hasattr(entry, field) and getattr(entry, field):
                date_str = getattr(entry, field)
                if not date_str:
                    continue
                    
                try:
                    # Handle ISO format with timezone
                    if 'T' in date_str:
                        date_str = date_str.replace('Z', '+00:00')
                        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    else:
                        # Try parsing with dateutil
                        from dateutil import parser as date_parser
                        return date_parser.parse(date_str)
                except Exception as e:
                    logger.debug(f"Failed to parse date string '{date_str}': {e}")
                    continue
        
        logger.warning(f"Could not parse date for entry: {entry.get('title', 'Unknown')}")
        return None
    
    def _extract_entry_data(
        self, 
        entry, 
        parser_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract data from RSS entry using parser configuration.
        
        Args:
            entry: Feed entry object
            parser_config: Parser configuration
            
        Returns:
            Dictionary with extracted entry data
        """
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
                if isinstance(entry.get('content'), list):
                    content_parts.append(entry.get('content', [{}])[0].get('value', ''))
                else:
                    content_parts.append(str(entry.get('content', '')))
            else:
                content_parts.append(entry.get(field, ''))
        
        content_text = '\n'.join(filter(None, content_parts))
        data['summary'] = content_text
        data['content'] = content_text
        
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
        
        # Clean up empty fields
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = value.strip()
        
        return data
