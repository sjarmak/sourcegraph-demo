import re
from datetime import datetime
from typing import Dict, List
from app.schemas import InsightCreate


class TextProcessor:
    """Processes raw text and extracts structured insights."""
    
    def __init__(self):
        self.tool_patterns = {
            "anthropic": ["anthropic", "claude", "ai assistant"],
            "openai": ["openai", "gpt", "chatgpt"],
            "sourcegraph": ["sourcegraph", "cody", "code search"],
            "github": ["github", "copilot", "actions"],
            "docker": ["docker", "container", "containerization"],
            "kubernetes": ["kubernetes", "k8s", "orchestration"],
            "aws": ["aws", "amazon web services", "cloud"],
            "google": ["google", "gcp", "cloud platform"],
            "microsoft": ["microsoft", "azure", "office"],
            "meta": ["meta", "facebook", "react"],
            "apple": ["apple", "ios", "macos"],
            "netflix": ["netflix", "streaming"],
            "uber": ["uber", "ride sharing"],
            "airbnb": ["airbnb", "accommodation"],
        }
    
    def extract_insight(self, raw_text: str) -> InsightCreate:
        """Extract structured insight from raw text."""
        # Clean the text
        cleaned_text = self._clean_text(raw_text)
        
        # Extract components
        tool = self._extract_tool(cleaned_text)
        date = self._extract_date(cleaned_text)
        title = self._extract_title(cleaned_text)
        summary = self._create_summary(cleaned_text)
        topics = self._extract_topics(cleaned_text)
        link = self._extract_link(raw_text)
        
        return InsightCreate(
            tool=tool,
            date=date,
            title=title,
            summary=summary,
            topics=topics,
            link=link
        )
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        return text
    
    def _extract_tool(self, text: str) -> str:
        """Extract tool name from text."""
        text_lower = text.lower()
        
        for tool, patterns in self.tool_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return tool
        
        # If no specific tool found, extract from first few words
        words = text.split()[:10]
        for word in words:
            if word.lower() in ["api", "sdk", "platform", "service", "tool"]:
                return "unknown"
        
        return "general"
    
    def _extract_date(self, text: str) -> datetime:
        """Extract date from text or use current date."""
        # Simple date patterns
        date_patterns = [
            r'\b(\d{4}[-/]\d{1,2}[-/]\d{1,2})\b',
            r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{4})\b',
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    # Try to parse the date (simplified)
                    return datetime.now()  # For now, return current date
                except:
                    continue
        
        return datetime.now()
    
    def _extract_title(self, text: str) -> str:
        """Extract title from text."""
        # Take first sentence or first 80 characters
        sentences = text.split('.')
        if sentences:
            title = sentences[0].strip()
            if len(title) > 80:
                title = title[:77] + "..."
            return title
        
        return text[:80] + "..." if len(text) > 80 else text
    
    def _create_summary(self, text: str) -> str:
        """Create summary from text."""
        # Simple summarization - take first paragraph or first 200 chars
        paragraphs = text.split('\n')
        if paragraphs and len(paragraphs[0]) > 50:
            summary = paragraphs[0]
        else:
            summary = text
        
        if len(summary) > 300:
            summary = summary[:297] + "..."
        
        return summary
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics/keywords from text."""
        text_lower = text.lower()
        
        # Common tech topics
        topic_keywords = [
            "ai", "machine learning", "artificial intelligence",
            "api", "sdk", "framework", "library",
            "cloud", "microservices", "container",
            "security", "authentication", "authorization",
            "database", "sql", "nosql",
            "frontend", "backend", "fullstack",
            "mobile", "web", "desktop",
            "deployment", "ci/cd", "devops",
            "performance", "optimization", "scaling",
            "analytics", "monitoring", "logging",
            "testing", "automation", "integration",
            "open source", "enterprise", "saas"
        ]
        
        found_topics = []
        for topic in topic_keywords:
            if topic in text_lower:
                # Special case for AI to keep proper capitalization
                if topic == "ai":
                    found_topics.append("AI")
                else:
                    found_topics.append(topic.title())
        
        # If no topics found, extract from first few sentences
        if not found_topics:
            words = text.split()[:50]
            for word in words:
                if len(word) > 4 and word.lower() not in ["the", "and", "for", "with", "this", "that"]:
                    found_topics.append(word.title())
                    if len(found_topics) >= 3:
                        break
        
        return found_topics[:5]  # Limit to 5 topics
    
    def _extract_link(self, text: str) -> str:
        """Extract URL from text."""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        match = re.search(url_pattern, text)
        return match.group(0) if match else None
    
    def extract_relevant_snippet(self, content: str, query: str = None, max_length: int = 200) -> str:
        """Extract most relevant snippet from content for highlighting."""
        if not content:
            return ""
        
        # Clean content
        content = re.sub(r'\s+', ' ', content.strip())
        
        if query:
            # Find sentences containing query terms
            query_words = query.lower().split()
            sentences = content.split('.')
            
            best_sentence = ""
            max_score = 0
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) < 20:  # Skip very short sentences
                    continue
                    
                score = sum(1 for word in query_words if word in sentence.lower())
                if score > max_score:
                    max_score = score
                    best_sentence = sentence
            
            if best_sentence and max_score > 0:
                # Truncate if too long
                if len(best_sentence) > max_length:
                    return best_sentence[:max_length-3] + "..."
                return best_sentence
        
        # Fallback: return first meaningful sentence or content chunk
        sentences = content.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) >= 20:
                if len(sentence) > max_length:
                    return sentence[:max_length-3] + "..."
                return sentence
        
        # Last resort: truncate content
        if len(content) > max_length:
            return content[:max_length-3] + "..."
        return content
