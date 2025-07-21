#!/usr/bin/env python3

import sys
import os
sys.path.append('backend')

from app.core.text_processor import TextProcessor

def test_smart_search():
    processor = TextProcessor()
    
    # Test cases from the actual search results
    test_cases = [
        {
            "title": "Built an AI Agent in n8n for YouTube Market Analysis",
            "content": "Built an AI Agent in n8n for YouTube Market Analysis – Great for Content Creators!png?width=1920&amp;format=png&amp;auto=webp&amp;s=dd788d8ebfe15a113d6bcd973cba8162c95fcfc3",
            "query": "Amp"
        },
        {
            "title": "All AI Coding Agents You Know", 
            "content": "All AI Coding Agents You KnowHere are a few examples to give you a sense of the range: Cursor (AI-native IDE) IDX/Firebase Studio (Google's web IDE) Replit Framework",
            "query": "Amp"
        },
        {
            "title": "Serverless Scaling: Deploying Strands + MCP on AWS",
            "content": "Serverless Scaling: Deploying Strands + MCP on AWS—Lambda (native &amp; web adapter) and Fargate", 
            "query": "Amp"
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n=== Test Case {i+1}: {test_case['title'][:50]}... ===")
        
        combined_text = f"{test_case['title']} {test_case['content']}"
        
        # Test cleaning
        clean_text = processor.clean_text_for_search(combined_text)
        print(f"Original text: {combined_text[:100]}...")
        print(f"Clean text: {clean_text[:100]}...")
        print(f"Contains 'amp': {'amp' in clean_text.lower()}")
        
        # Test scoring
        score = processor.score_text_relevance(combined_text, test_case['query'])
        print(f"Relevance score: {score}")
        
        # Test snippet extraction
        snippet = processor.extract_relevant_snippet(
            combined_text, test_case['query'], max_length=300, highlight=True
        )
        print(f"Smart snippet: {snippet}")
        print(f"Contains <mark>: {'<mark>' in snippet}")
        
        # Test the new keyword context extraction directly
        context_snippet = processor.extract_keyword_context_snippet(
            combined_text, test_case['query'], words_around=50
        )
        print(f"Context snippet: {context_snippet}")
        print(f"Context contains <mark>: {'<mark>' in context_snippet}")

if __name__ == "__main__":
    test_smart_search()
