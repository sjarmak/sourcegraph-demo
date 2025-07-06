"""
arXiv source handler for the Agentic Insight Tracker.
"""
import feedparser
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import aiohttp
from urllib.parse import quote_plus

from .base import BaseSource

logger = logging.getLogger(__name__)


class ArxivSource(BaseSource):
    """
    arXiv API source handler.
    
    Fetches papers from arXiv based on search terms and categories.
    Uses the arXiv API which returns Atom feeds.
    """
    
    async def fetch(
        self, 
        session: aiohttp.ClientSession, 
        cutoff_time: datetime
    ) -> List[Dict[str, Any]]:
        """
        Fetch and process arXiv papers.
        
        Args:
            session: HTTP session for making requests
            cutoff_time: Only return entries newer than this time
            
        Returns:
            List of processed papers that match keywords and are recent
        """
        try:
            # Build arXiv API query
            query_url = self._build_arxiv_query()
            
            # Fetch results
            content = await self._make_request(session, query_url, timeout=45)
            
            # Parse Atom feed
            feed = feedparser.parse(content)
            
            if feed.bozo and feed.bozo_exception:
                logger.warning(f"arXiv feed parsing warning for {self.name}: {feed.bozo_exception}")
            
            if not feed.entries:
                logger.warning(f"No entries found in arXiv feed for {self.name}")
                return []
            
            processed_entries = []
            
            for entry in feed.entries:
                try:
                    # Parse entry date
                    entry_date = self._parse_arxiv_date(entry)
                    if not entry_date:
                        continue
                    
                    # Check if paper is recent enough
                    if not self._is_entry_recent(entry_date, cutoff_time):
                        continue
                    
                    # Extract paper data
                    processed_entry = self._extract_arxiv_data(entry)
                    processed_entry['published'] = entry_date
                    
                    # Apply keyword filtering
                    filtered_entry = self._apply_keyword_filter(processed_entry)
                    if filtered_entry:
                        processed_entries.append(filtered_entry)
                
                except Exception as e:
                    logger.error(f"Error processing arXiv entry from {self.name}: {e}")
                    continue
            
            logger.info(f"Found {len(processed_entries)} relevant papers from {self.name}")
            return processed_entries
            
        except Exception as e:
            logger.error(f"Error fetching arXiv papers for {self.name}: {e}")
            return []
    
    def _build_arxiv_query(self) -> str:
        """
        Build arXiv API query URL based on configuration.
        
        Returns:
            Complete arXiv API query URL
        """
        base_url = "http://export.arxiv.org/api/query"
        
        # Get search configuration
        search_terms = self.config.get("search_terms", [])
        categories = self.config.get("categories", ["cs.AI", "cs.SE", "cs.LG", "stat.ML"])
        max_results = self.config.get("max_results", 100)
        sort_by = self.config.get("sort_by", "submittedDate")
        sort_order = self.config.get("sort_order", "descending")
        
        # Build search query
        query_parts = []
        
        # Add category filters
        if categories:
            category_query = " OR ".join([f"cat:{cat}" for cat in categories])
            query_parts.append(f"({category_query})")
        
        # Add search terms (search in title and abstract)
        if search_terms:
            # Create search term combinations for title and abstract
            term_queries = []
            for term in search_terms:
                term_queries.append(f'ti:"{term}"')
                term_queries.append(f'abs:"{term}"')
            
            if term_queries:
                query_parts.append(f"({' OR '.join(term_queries)})")
        
        # Combine all query parts
        if query_parts:
            search_query = " AND ".join(query_parts)
        else:
            # Fallback to category search only
            search_query = " OR ".join([f"cat:{cat}" for cat in categories])
        
        # URL encode the query
        encoded_query = quote_plus(search_query)
        
        # Build final URL
        query_url = (
            f"{base_url}?"
            f"search_query={encoded_query}&"
            f"start=0&"
            f"max_results={max_results}&"
            f"sortBy={sort_by}&"
            f"sortOrder={sort_order}"
        )
        
        logger.debug(f"arXiv query URL for {self.name}: {query_url}")
        return query_url
    
    def _parse_arxiv_date(self, entry) -> Optional[datetime]:
        """
        Parse arXiv entry date.
        
        Args:
            entry: arXiv entry object
            
        Returns:
            Parsed datetime or None if parsing fails
        """
        # arXiv uses 'published' and 'updated' fields
        date_fields = ["published_parsed", "updated_parsed"]
        
        for field in date_fields:
            if hasattr(entry, field) and getattr(entry, field):
                try:
                    time_struct = getattr(entry, field)
                    if time_struct and len(time_struct) >= 6:
                        return datetime(*time_struct[:6])
                except Exception as e:
                    logger.debug(f"Failed to parse arXiv {field}: {e}")
                    continue
        
        # Fallback to string parsing
        for field in ["published", "updated"]:
            if hasattr(entry, field) and getattr(entry, field):
                date_str = getattr(entry, field)
                try:
                    # arXiv dates are typically in ISO format
                    if 'T' in date_str:
                        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    else:
                        from dateutil import parser as date_parser
                        return date_parser.parse(date_str)
                except Exception as e:
                    logger.debug(f"Failed to parse arXiv date string '{date_str}': {e}")
                    continue
        
        logger.warning(f"Could not parse date for arXiv entry: {entry.get('title', 'Unknown')}")
        return None
    
    def _extract_arxiv_data(self, entry) -> Dict[str, Any]:
        """
        Extract data from arXiv entry.
        
        Args:
            entry: arXiv entry object
            
        Returns:
            Dictionary with extracted paper data
        """
        data = {}
        
        # Extract title (remove newlines and extra spaces)
        title = entry.get('title', '').replace('\n', ' ').strip()
        data['title'] = ' '.join(title.split())
        
        # Extract abstract/summary (clean up formatting)
        summary = entry.get('summary', '').replace('\n', ' ').strip()
        data['summary'] = ' '.join(summary.split())
        data['content'] = data['summary']  # For arXiv, content is the abstract
        
        # Extract arXiv link
        data['link'] = entry.get('link', '')
        
        # Extract authors
        authors = []
        if entry.get('authors'):
            for author in entry.get('authors', []):
                if isinstance(author, dict):
                    authors.append(author.get('name', ''))
                else:
                    authors.append(str(author))
        data['author'] = ', '.join(authors)
        
        # Extract categories as tags
        tags = []
        if entry.get('tags'):
            for tag in entry.get('tags', []):
                if isinstance(tag, dict):
                    tags.append(tag.get('term', ''))
                else:
                    tags.append(str(tag))
        data['tags'] = tags
        
        # Extract arXiv ID from link
        arxiv_id = ''
        link = data['link']
        if 'arxiv.org/abs/' in link:
            arxiv_id = link.split('arxiv.org/abs/')[-1]
        data['arxiv_id'] = arxiv_id
        
        # Extract DOI if available
        doi = ''
        if hasattr(entry, 'arxiv_doi') and entry.arxiv_doi:
            doi = entry.arxiv_doi
        data['doi'] = doi
        
        # Add arXiv-specific metadata
        data['source_metadata'] = {
            'arxiv_id': arxiv_id,
            'doi': doi,
            'categories': tags,
            'authors': authors,
            'type': 'research_paper'
        }
        
        return data
