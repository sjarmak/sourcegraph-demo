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
    
    def clean_text_for_search(self, text: str) -> str:
        """Clean text for contextual search by removing URLs and HTML entities."""
        if not text:
            return ""
        
        # HTML unescape (turns "&amp;" → "&")
        import html
        text = html.unescape(text)
        
        # Remove URLs
        text = re.sub(r'https?://\S+', ' ', text)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Remove punctuation and normalize spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def score_text_relevance(self, text: str, query: str) -> float:
        """Score text relevance for contextual search queries like 'Amp'."""
        if not query or not text:
            return 0.0
        
        # Clean text to remove URL artifacts
        clean_text = self.clean_text_for_search(text).lower()
        query_lower = query.lower()
        
        # Context words that indicate AI/coding relevance
        context_words = {
            'ai', 'artificial intelligence', 'code', 'coding', 'programming', 
            'developer', 'development', 'agent', 'agentic', 'llm', 'language model',
            'tool', 'assistant', 'copilot', 'framework', 'library', 'ide', 'editor',
            'automation', 'machine learning', 'neural', 'model', 'chatgpt', 'openai',
            'github', 'cursor', 'vscode', 'replit', 'claude', 'anthropic'
        }
        
        # Find occurrences of the query term as standalone words
        import re
        query_pattern = rf'\b{re.escape(query_lower)}\b'
        query_matches = re.findall(query_pattern, clean_text)
        
        if not query_matches:
            return 0.0
        
        score = 0.0
        
        # Score each occurrence based on context
        for match in re.finditer(query_pattern, clean_text):
            pos = match.start()
            
            # Get context window around the match (50 chars each side)
            window_start = max(0, pos - 50)
            window_end = min(len(clean_text), pos + 50)
            context_window = clean_text[window_start:window_end]
            
            # Check if this match is in an irrelevant context (like URLs or random text)
            if any(artifact in context_window for artifact in ['format png', 'auto webp', 'width height']):
                continue  # Skip URL-like contexts
            
            # Base score for each relevant occurrence
            match_score = 10.0
            
            # Boost score for each context word found nearby
            context_hits = sum(1 for word in context_words if word in context_window)
            match_score += context_hits * 5.0
            
            # Extra boost if multiple context words appear together
            if context_hits >= 2:
                match_score += 10.0
                
            score = max(score, match_score)
        
        return score

    def extract_relevant_snippet(self, content: str, query: str = None, max_length: int = 200, highlight: bool = True) -> str:
        """Extract most relevant snippet from content with smart contextual highlighting."""
        if not content:
            return ""
        
        # Clean content
        content = re.sub(r'\s+', ' ', content.strip())
        
        if query:
            # Score relevance and find best matching position
            relevance_score = self.score_text_relevance(content, query)
            
            if relevance_score > 0:
                # Find the best contextual match for highlighting
                clean_text = self.clean_text_for_search(content).lower()
                query_lower = query.lower()
                query_pattern = rf'\b{re.escape(query_lower)}\b'
                
                best_pos = None
                best_score = 0
                
                # Find the best match position with good context
                for match in re.finditer(query_pattern, clean_text):
                    pos = match.start()
                    window_start = max(0, pos - 50)
                    window_end = min(len(clean_text), pos + 50)
                    context_window = clean_text[window_start:window_end]
                    
                    # Skip URL-like contexts
                    if any(artifact in context_window for artifact in ['format png', 'auto webp', 'width height']):
                        continue
                    
                    # Count context words
                    context_words = {
                        'ai', 'code', 'coding', 'programming', 'developer', 'agent', 
                        'agentic', 'llm', 'tool', 'assistant', 'framework'
                    }
                    context_hits = sum(1 for word in context_words if word in context_window)
                    
                    if context_hits > best_score:
                        best_score = context_hits
                        # Map back to original text position (approximately)
                        best_pos = pos
                
                if best_pos is not None:
                    # Extract snippet around the best match
                    snippet_start = max(0, best_pos - 100)
                    snippet_end = min(len(content), best_pos + 100)
                    best_snippet = content[snippet_start:snippet_end].strip()
                    
                    # Add highlighting if requested, but only for contextually relevant matches
                    if highlight:
                        # Only highlight the query term when it appears in meaningful context
                        pattern = rf'\b({re.escape(query)})\b'
                        
                        # Check each match before highlighting
                        def highlight_match(match):
                            match_text = match.group(0)
                            match_start = match.start()
                            
                            # Get context around this specific match
                            context_start = max(0, match_start - 30)
                            context_end = min(len(best_snippet), match_start + 30)
                            local_context = best_snippet[context_start:context_end].lower()
                            
                            # Skip highlighting if it's in URL-like context
                            if any(artifact in local_context for artifact in ['&amp', 'format=', 'width=', 'auto=webp']):
                                return match_text  # Return unhighlighted
                            
                            return f'<mark>{match_text}</mark>'
                        
                        best_snippet = re.sub(pattern, highlight_match, best_snippet, flags=re.IGNORECASE)
                    
                    # Truncate if too long
                    if len(best_snippet) > max_length:
                        return best_snippet[:max_length-3] + "..."
                    return best_snippet
        
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
