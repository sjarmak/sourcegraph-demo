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

    def extract_keyword_context_snippet(self, content: str, query: str, words_around: int = 50) -> str:
        """Extract snippet showing keyword in context with surrounding words."""
        if not content or not query:
            return ""
        
        # Normalize text and query
        normalized_content = re.sub(r'\s+', ' ', content.strip())
        query_words = [w.strip().lower() for w in query.split() if w.strip()]
        
        if not query_words:
            return normalized_content[:200] + "..." if len(normalized_content) > 200 else normalized_content
        
        # Find all matches for any query word
        best_match = None
        best_score = 0
        
        for query_word in query_words:
            # Skip very short words
            if len(query_word) < 3:
                continue
                
            # Find all occurrences of this word (case insensitive)
            pattern = rf'\b{re.escape(query_word)}\b'
            
            for match in re.finditer(pattern, normalized_content, re.IGNORECASE):
                match_pos = match.start()
                match_text = match.group(0)
                
                # Get context around the match
                words = normalized_content.split()
                
                # Find word position
                word_positions = []
                current_pos = 0
                for i, word in enumerate(words):
                    word_start = normalized_content.find(word, current_pos)
                    word_end = word_start + len(word)
                    word_positions.append((word_start, word_end, i))
                    current_pos = word_end
                
                # Find which word contains our match
                match_word_idx = None
                for word_start, word_end, word_idx in word_positions:
                    if word_start <= match_pos < word_end:
                        match_word_idx = word_idx
                        break
                
                if match_word_idx is not None:
                    # Extract surrounding words
                    start_word = max(0, match_word_idx - words_around)
                    end_word = min(len(words), match_word_idx + words_around + 1)
                    
                    context_words = words[start_word:end_word]
                    context_snippet = ' '.join(context_words)
                    
                    # Check if this is in a URL or other irrelevant context
                    context_lower = context_snippet.lower()
                    if any(artifact in context_lower for artifact in [
                        'format=png', 'auto=webp', 'width=', 'height=', '&amp;', 'https://'
                    ]):
                        continue  # Skip URL contexts
                    
                    # Score this match based on coding context
                    context_words_set = {
                        'ai', 'artificial intelligence', 'code', 'coding', 'programming', 
                        'developer', 'development', 'agent', 'agentic', 'llm', 'language model',
                        'tool', 'assistant', 'copilot', 'framework', 'library', 'ide', 'editor',
                        'automation', 'machine learning', 'model', 'github', 'cursor'
                    }
                    
                    score = sum(1 for word in context_words_set if word in context_lower)
                    
                    if score > best_score:
                        best_score = score
                        best_match = {
                            'snippet': context_snippet,
                            'query_word': query_word,
                            'match_text': match_text
                        }
        
        if best_match:
            snippet = best_match['snippet']
            query_word = best_match['query_word']
            
            # Highlight the matched term
            pattern = rf'\b({re.escape(query_word)})\b'
            highlighted_snippet = re.sub(pattern, r'<mark>\1</mark>', snippet, flags=re.IGNORECASE)
            
            return highlighted_snippet
        
        # Fallback: no good matches found, return beginning of content
        return normalized_content[:200] + "..." if len(normalized_content) > 200 else normalized_content

    def extract_relevant_snippet(self, content: str, query: str = None, max_length: int = 200, highlight: bool = True) -> str:
        """Extract most relevant snippet from content with smart contextual highlighting."""
        if not content:
            return ""
        
        if query and highlight:
            # Use the new keyword context extraction
            context_snippet = self.extract_keyword_context_snippet(content, query, words_around=50)
            if context_snippet and '<mark>' in context_snippet:
                # Truncate if too long
                if len(context_snippet) > max_length:
                    return context_snippet[:max_length-3] + "..."
                return context_snippet
        
        # Fallback to original logic
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Return first meaningful sentence or content chunk
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
