"""
Tool detection utility for identifying coding agents and AI tools mentioned in content.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Set

logger = logging.getLogger(__name__)


class ToolDetector:
    """
    Detects coding agents and AI tools mentioned in content.
    
    Maps keyword variations to canonical tool names and concepts.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize tool detector.
        
        Args:
            config_path: Path to tool aliases configuration file
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "tool_aliases.json"
        
        self.config_path = config_path
        self.tool_aliases = {}
        self.concept_keywords = {}
        self._load_config()
    
    def _load_config(self):
        """Load tool aliases configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            self.tool_aliases = config.get("tool_aliases", {})
            self.concept_keywords = config.get("concept_keywords", {})
            
            logger.info(f"Loaded {len(self.tool_aliases)} tool aliases and {len(self.concept_keywords)} concept groups")
            
        except Exception as e:
            logger.error(f"Error loading tool aliases config from {self.config_path}: {e}")
            self.tool_aliases = {}
            self.concept_keywords = {}
    
    def detect_tools(self, matched_keywords: List[str]) -> List[str]:
        """
        Detect canonical tools from matched keywords.
        
        Args:
            matched_keywords: List of matched keywords from keyword filter
            
        Returns:
            List of canonical tool names detected in the content
        """
        detected_tools = set()
        
        # Convert keywords to lowercase for case-insensitive matching
        keywords_lower = [k.lower() for k in matched_keywords]
        
        # Check each tool's aliases
        for canonical_tool, aliases in self.tool_aliases.items():
            for alias in aliases:
                if alias.lower() in keywords_lower:
                    detected_tools.add(canonical_tool)
                    break  # Found a match for this tool, move to next
        
        return list(detected_tools)
    
    def detect_concepts(self, matched_keywords: List[str]) -> List[str]:
        """
        Detect AI/coding concepts from matched keywords.
        
        Args:
            matched_keywords: List of matched keywords from keyword filter
            
        Returns:
            List of canonical concept names detected in the content
        """
        detected_concepts = set()
        
        # Convert keywords to lowercase for case-insensitive matching
        keywords_lower = [k.lower() for k in matched_keywords]
        
        # Check each concept's keywords
        for canonical_concept, keywords in self.concept_keywords.items():
            for keyword in keywords:
                if keyword.lower() in keywords_lower:
                    detected_concepts.add(canonical_concept)
                    break  # Found a match for this concept, move to next
        
        return list(detected_concepts)
    
    def get_all_tool_keywords(self) -> Set[str]:
        """Get all tool-related keywords for filtering."""
        all_keywords = set()
        
        for aliases in self.tool_aliases.values():
            all_keywords.update(alias.lower() for alias in aliases)
        
        for keywords in self.concept_keywords.values():
            all_keywords.update(keyword.lower() for keyword in keywords)
        
        return all_keywords
    
    def get_canonical_tools(self) -> List[str]:
        """Get list of all canonical tool names."""
        return list(self.tool_aliases.keys())
    
    def get_canonical_concepts(self) -> List[str]:
        """Get list of all canonical concept names."""
        return list(self.concept_keywords.keys())
