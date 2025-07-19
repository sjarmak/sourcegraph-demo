"""
Base class for source handlers in the Agentic Insight Tracker.
"""
import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any
import aiohttp
import logging

from app.core.keyword_filter import KeywordFilter

logger = logging.getLogger(__name__)


class BaseSource(ABC):
    """
    Abstract base class for all source handlers.
    
    Each source type (RSS, arXiv, Reddit API, etc.) should implement this interface
    to provide consistent data extraction and keyword filtering.
    """
    
    def __init__(self, config: Dict[str, Any], keyword_filter: KeywordFilter):
        """
        Initialize source handler.
        
        Args:
            config: Source configuration from sources.json
            keyword_filter: Centralized keyword filtering engine
        """
        self.config = config
        self.keyword_filter = keyword_filter
        self.name = config["name"]
        self.enabled = config.get("enabled", True)
        self.source_type = config.get("type", "unknown")
        
        logger.debug(f"Initialized {self.__class__.__name__} for source: {self.name}")
    
    @abstractmethod
    async def fetch(
        self, 
        session: aiohttp.ClientSession, 
        cutoff_time: datetime
    ) -> List[Dict[str, Any]]:
        """
        Fetch and process entries from this source.
        
        Args:
            session: HTTP session for making requests
            cutoff_time: Only return entries newer than this time
            
        Returns:
            List of processed entries with the following format:
            {
                "title": str,
                "summary": str,
                "content": str,
                "link": str,
                "published": datetime,
                "tags": List[str],
                "matched_keywords": List[str],  # Keywords that caused this to be kept
                "author": str (optional),
                "source_metadata": Dict (optional)
            }
        """
        pass
    
    def _build_text_for_filtering(self, entry: Dict[str, Any]) -> str:
        """
        Build text content for keyword filtering.
        
        Args:
            entry: Raw entry data
            
        Returns:
            Combined text to check for keywords
        """
        text_parts = []
        
        # Add title
        if entry.get('title'):
            text_parts.append(entry['title'])
        
        # Add summary/description
        if entry.get('summary'):
            text_parts.append(entry['summary'])
        
        # Add content if available
        if entry.get('content'):
            text_parts.append(entry['content'])
        
        # Add tags
        tags = entry.get('tags', [])
        if tags:
            text_parts.append(' '.join(tags))
        
        # Add author if available
        if entry.get('author'):
            text_parts.append(entry['author'])
        
        return ' '.join(text_parts)
    
    def _apply_keyword_filter(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply keyword filtering to an entry.
        
        Args:
            entry: Entry to filter
            
        Returns:
            Entry with matched_keywords added, or None if no keywords matched
        """
        text_for_filtering = self._build_text_for_filtering(entry)
        matched_keywords = self.keyword_filter.match(self.name, text_for_filtering)
        
        if matched_keywords:
            entry['matched_keywords'] = matched_keywords
            return entry
        else:
            # Entry doesn't match any keywords, filter it out
            return None
    
    def _is_entry_recent(self, entry_date: datetime, cutoff_time: datetime) -> bool:
        """
        Check if entry is recent enough to include.
        
        Args:
            entry_date: Date of the entry
            cutoff_time: Cutoff time for filtering
            
        Returns:
            True if entry is recent enough, False otherwise
        """
        return entry_date > cutoff_time
    
    async def _make_request(
        self, 
        session: aiohttp.ClientSession, 
        url: str,
        timeout: int = 30,
        **kwargs
    ) -> str:
        """
        Make HTTP request with error handling.
        
        Args:
            session: HTTP session
            url: URL to fetch
            timeout: Request timeout in seconds
            **kwargs: Additional arguments for the request
            
        Returns:
            Response text
            
        Raises:
            Exception: If request fails
        """
        try:
            # Ensure we have proper headers to avoid being blocked by Cloudflare
            headers = kwargs.get('headers', {})
            if 'User-Agent' not in headers:
                headers['User-Agent'] = 'AITrackerBot/1.0 (Agentic Insight Tracker; +https://github.com/your-org/ai-tracker)'
            headers['Accept'] = 'application/rss+xml, application/xml, text/xml, */*'
            headers['Accept-Encoding'] = 'gzip, deflate'
            kwargs['headers'] = headers
            
            timeout_config = aiohttp.ClientTimeout(total=timeout)
            async with session.get(url, timeout=timeout_config, **kwargs) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    raise Exception(f"HTTP {response.status} error for {url}")
        except asyncio.TimeoutError:
            raise Exception(f"Timeout error for {url}")
        except Exception as e:
            raise Exception(f"Request error for {url}: {e}")
    
    def get_source_info(self) -> Dict[str, Any]:
        """Get information about this source."""
        return {
            "name": self.name,
            "type": self.source_type,
            "enabled": self.enabled,
            "endpoint": self.config.get("endpoint"),
            "keywords": len(self.keyword_filter.get_keywords_for_source(self.name))
        }
