#!/usr/bin/env python3

import sys
import os
sys.path.append('backend')

from app.core.text_processor import TextProcessor

def test_context_snippets():
    processor = TextProcessor()
    
    # Test cases with explicit "Amp" mentions in coding context
    test_cases = [
        {
            "title": "All AI Coding Agents You Know",
            "content": "All AI Coding Agents You Know. Here are a few examples to give you a sense of the range: Cursor (AI-native IDE) IDX/Firebase Studio (Google's web IDE) Replit Framework and Amp coding assistant for developers working on AI projects. The Amp tool helps with code generation and programming tasks.",
            "query": "Amp"
        },
        {
            "title": "Top AI Development Tools",
            "content": "Top AI Development Tools include various programming assistants. Some popular ones are GitHub Copilot, Cursor, and Amp which is an excellent coding agent for developers. Amp provides intelligent code suggestions and helps with complex programming tasks.",
            "query": "Amp"  
        },
        {
            "title": "Random Article with URL",
            "content": "Some random article with a URL like https://example.com?width=1920&amp;format=png&amp;auto=webp which contains amp but not in coding context.",
            "query": "Amp"
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n=== Test Case {i+1}: {test_case['title']} ===")
        
        combined_text = f"{test_case['title']} {test_case['content']}"
        print(f"Full text: {combined_text}")
        
        # Test new context snippet extraction
        context_snippet = processor.extract_keyword_context_snippet(
            combined_text, test_case['query'], words_around=25
        )
        print(f"\nContext snippet (25 words): {context_snippet}")
        print(f"Contains <mark>: {'<mark>' in context_snippet}")
        
        # Test with more words
        context_snippet_50 = processor.extract_keyword_context_snippet(
            combined_text, test_case['query'], words_around=50
        )
        print(f"\nContext snippet (50 words): {context_snippet_50}")
        print(f"Contains <mark>: {'<mark>' in context_snippet_50}")
        
        # Test the main extract_relevant_snippet function
        relevant_snippet = processor.extract_relevant_snippet(
            combined_text, test_case['query'], max_length=300, highlight=True
        )
        print(f"\nRelevant snippet: {relevant_snippet}")
        print(f"Contains <mark>: {'<mark>' in relevant_snippet}")

if __name__ == "__main__":
    test_context_snippets()
