"""
Centralized keyword filtering for content relevance detection.
"""
import json
import logging
import re
from pathlib import Path
from typing import List, Dict, Set, Optional

logger = logging.getLogger(__name__)


class KeywordFilter:
    """
    Centralized keyword filtering engine for determining content relevance.
    
    Supports global keywords and per-source overrides for flexible filtering.
    """
    
    def __init__(
        self,
        global_keywords: Optional[List[str]] = None,
        per_source_overrides: Optional[Dict[str, List[str]]] = None
    ):
        """
        Initialize keyword filter.
        
        Args:
            global_keywords: List of keywords to match across all sources
            per_source_overrides: Source-specific keyword overrides
        """
        self.global_keywords = {k.lower() for k in (global_keywords or [])}
        self.overrides = {
            source: {k.lower() for k in keywords}
            for source, keywords in (per_source_overrides or {}).items()
        }
        
        logger.info(f"KeywordFilter initialized with {len(self.global_keywords)} global keywords")
    
    @classmethod
    def from_config_file(cls, config_path: Optional[str] = None) -> "KeywordFilter":
        """
        Create KeywordFilter from configuration file.
        
        Args:
            config_path: Path to keywords configuration file
            
        Returns:
            Configured KeywordFilter instance
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "keywords.json"
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            global_keywords = config.get("global_keywords", [])
            per_source_overrides = config.get("per_source_keywords", {})
            
            return cls(global_keywords, per_source_overrides)
            
        except Exception as e:
            logger.error(f"Error loading keyword config from {config_path}: {e}")
            # Return empty filter as fallback
            return cls()
    
    def match_content(self, source_name: str, text: str) -> List[str]:
        """
        Check content text (title, summary, body) for contextual keyword matches.
        
        Args:
            source_name: Name of the source
            text: Content text to check
            
        Returns:
            List of matched keywords with contextual validation
        """
        if not text:
            return []
        
        keywords_to_check = self.global_keywords | self.overrides.get(source_name, set())
        if not keywords_to_check:
            return []
        
        text_lower = text.lower()
        matched = []
        
        # Coding agent context keywords
        coding_context = ["coding", "agent", "assistant", "ai", "programming", "developer", "sourcegraph", "cody", "copilot", "ide", "editor", "code", "development"]
        has_coding_context = any(ctx in text_lower for ctx in coding_context)
        
        for keyword in keywords_to_check:
            # Special handling for "amp" - must be capitalized and in coding context
            if keyword == "amp":
                # Only match "Amp", "AMP", or "AmpCode" in coding context
                if has_coding_context:
                    if re.search(r'\b(Amp|AMP|AmpCode)\b', text):
                        matched.append(keyword)
            # Special handling for other short ambiguous keywords
            elif keyword in ["ai", "ml", "qa", "ci", "cd"]:
                # Use word boundaries and require some context
                if re.search(rf'\b{re.escape(keyword.upper())}\b', text) or re.search(rf'\b{re.escape(keyword)}\b', text_lower):
                    matched.append(keyword)
            # All other keywords - use word boundaries to avoid matching in URLs
            else:
                # Use word boundaries for all keywords to avoid matching in URLs/paths
                if re.search(rf'\b{re.escape(keyword)}\b', text_lower):
                    matched.append(keyword)
        
        return matched
    
    def match_domain(self, source_name: str, domain_text: str) -> List[str]:
        """
        Check domain/URL context for vendor-specific keywords.
        
        Args:
            source_name: Name of the source
            domain_text: Domain/URL text to check
            
        Returns:
            List of matched vendor keywords
        """
        if not domain_text:
            return []
        
        keywords_to_check = self.global_keywords | self.overrides.get(source_name, set())
        if not keywords_to_check:
            return []
        
        domain_lower = domain_text.lower()
        matched = []
        
        # Only match vendor/domain keywords in URLs
        vendor_keywords = ["sourcegraph", "github", "openai", "anthropic", "microsoft", "google", "aws"]
        
        for keyword in keywords_to_check:
            if keyword in vendor_keywords and keyword in domain_lower:
                matched.append(keyword)
        
        return matched
    
    def match(self, source_name: str, text: str) -> List[str]:
        """
        Legacy method for backward compatibility.
        """
        return self.match_content(source_name, text)
    
    def is_relevant(self, source_name: str, text: str) -> bool:
        """
        Check if text is relevant based on keyword matching.
        
        Args:
            source_name: Name of the source
            text: Text content to check
            
        Returns:
            True if text contains any matching keywords, False otherwise
        """
        return len(self.match(source_name, text)) > 0
    
    def get_keywords_for_source(self, source_name: str) -> Set[str]:
        """
        Get the effective keyword set for a specific source.
        
        Args:
            source_name: Name of the source
            
        Returns:
            Set of keywords that will be checked for this source
        """
        return self.global_keywords | self.overrides.get(source_name, set())
    
    def add_global_keywords(self, keywords: List[str]) -> None:
        """
        Add keywords to the global keyword set.
        
        Args:
            keywords: List of keywords to add
        """
        self.global_keywords.update(k.lower() for k in keywords)
    
    def add_source_keywords(self, source_name: str, keywords: List[str]) -> None:
        """
        Add keywords for a specific source.
        
        Args:
            source_name: Name of the source
            keywords: List of keywords to add for this source
        """
        if source_name not in self.overrides:
            self.overrides[source_name] = set()
        self.overrides[source_name].update(k.lower() for k in keywords)
    
    def get_all_keywords(self) -> Set[str]:
        """Get all keywords across all sources."""
        all_keywords = self.global_keywords.copy()
        for source_keywords in self.overrides.values():
            all_keywords.update(source_keywords)
        return all_keywords
