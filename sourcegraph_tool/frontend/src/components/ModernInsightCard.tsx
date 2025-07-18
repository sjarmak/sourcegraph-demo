import { format } from 'date-fns';
import { ExternalLink, Calendar, Tag, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';
import type { Insight } from '../types';

interface ModernInsightCardProps {
  insight: Insight;
  searchQuery?: string;
}

export const ModernInsightCard = ({ insight, searchQuery }: ModernInsightCardProps) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  const sourceColors = {
    anthropic: 'bg-orange-100 text-orange-700 border-orange-200',
    openai: 'bg-green-100 text-green-700 border-green-200',
    sourcegraph: 'bg-blue-100 text-blue-700 border-blue-200',
    github: 'bg-gray-100 text-gray-700 border-gray-200',
    dev_to: 'bg-purple-100 text-purple-700 border-purple-200',
    hackernews: 'bg-orange-100 text-orange-700 border-orange-200',
    reddit_machinelearning: 'bg-red-100 text-red-700 border-red-200',
    product_hunt: 'bg-pink-100 text-pink-700 border-pink-200',
    aws: 'bg-yellow-100 text-yellow-700 border-yellow-200',
    google: 'bg-blue-100 text-blue-700 border-blue-200',
    microsoft: 'bg-blue-100 text-blue-700 border-blue-200',
    meta: 'bg-blue-100 text-blue-700 border-blue-200',
    netflix: 'bg-red-100 text-red-700 border-red-200',
    uber: 'bg-gray-100 text-gray-700 border-gray-200',
    airbnb: 'bg-red-100 text-red-700 border-red-200',
    default: 'bg-gray-100 text-gray-700 border-gray-200'
  };

  const getSourceColor = (tool: string) => {
    return sourceColors[tool as keyof typeof sourceColors] || sourceColors.default;
  };

  // Clean and prepare text for display
  const cleanText = (text: string) => {
    // Remove HTML tags and markdown links
    return text
      .replace(/<[^>]*>/g, '') // Remove HTML tags
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Convert markdown links to just text
      .replace(/Article URL:.*$/gm, '') // Remove "Article URL:" lines
      .replace(/Source:.*$/gm, '') // Remove "Source:" lines
      .replace(/Link:.*$/gm, '') // Remove "Link:" lines
      .replace(/URL:.*$/gm, '') // Remove "URL:" lines
      .replace(/https?:\/\/[^\s]+/g, '') // Remove standalone URLs
      .replace(/\n\s*\n/g, '\n') // Remove multiple newlines
      .replace(/^\s*[-*]\s*/gm, '') // Remove bullet points
      .replace(/Title:\s*/gi, '') // Remove "Title:" prefix
      .replace(/Summary:\s*/gi, '') // Remove "Summary:" prefix
      .trim();
  };

  // Use snippet if available, otherwise fall back to summary, with better fallback
  const rawText = insight.snippet || insight.summary || insight.title || '';
  const displayText = cleanText(rawText);
  
  // If displayText is too short or empty, try to extract more context from summary
  const finalDisplayText = displayText.length < 50 && insight.summary && insight.summary !== rawText 
    ? cleanText(insight.summary)
    : displayText;
  
  // Smart truncation at sentence boundaries
  const truncateAtSentence = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text;
    
    const truncated = text.substring(0, maxLength);
    const lastSentence = truncated.lastIndexOf('. ');
    const lastQuestion = truncated.lastIndexOf('? ');
    const lastExclamation = truncated.lastIndexOf('! ');
    
    const lastPunctuation = Math.max(lastSentence, lastQuestion, lastExclamation);
    
    if (lastPunctuation > maxLength * 0.7) { // If we can cut at a sentence and keep at least 70% of content
      return truncated.substring(0, lastPunctuation + 1);
    }
    
    return truncated + '...';
  };

  const shouldShowExpand = finalDisplayText.length > 200;
  const truncatedText = shouldShowExpand && !isExpanded 
    ? truncateAtSentence(finalDisplayText, 200)
    : finalDisplayText;

  // Highlight keywords in text
  const highlightText = (text: string, query?: string) => {
    if (!query || !text) return text;
    
    // Split query into individual words and filter out short words
    const keywords = query.toLowerCase().split(/\s+/).filter(k => k.length > 2);
    let highlightedText = text;
    
    keywords.forEach(keyword => {
      // Escape special regex characters and create word boundary regex
      const escapedKeyword = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const regex = new RegExp(`\\b(${escapedKeyword})\\b`, 'gi');
      highlightedText = highlightedText.replace(regex, '<strong class="bg-yellow-200 px-1 rounded">$1</strong>');
    });
    
    return highlightedText;
  };

  const finalText = highlightText(truncatedText, searchQuery);

  // Filter out common/generic topics since all content is AI-related
  const filteredTopics = insight.topics?.filter(topic => {
    const lowerTopic = topic.toLowerCase().trim();
    return lowerTopic !== 'ai' && 
           lowerTopic !== 'artificial intelligence' &&
           lowerTopic !== 'title' &&
           lowerTopic !== 'title:' &&
           lowerTopic !== 'summary' &&
           lowerTopic !== 'summary:' &&
           lowerTopic !== 'article' &&
           lowerTopic !== 'link' &&
           lowerTopic !== 'url' &&
           lowerTopic.length > 1; // Filter out single character topics
  }) || [];

  return (
    <div 
      className="bg-white border border-neutral-200 rounded-lg hover:bg-neutral-50 hover:border-neutral-300 transition-all duration-200 group"
    >
      {/* Header bar */}
      <div className="flex items-center justify-between p-4 pb-3 border-b border-neutral-100">
        <div className="flex items-center gap-2">
          <span className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium border ${getSourceColor(insight.tool)}`}>
            {insight.tool.replace(/_/g, ' ').replace(/([A-Z])/g, ' $1').trim()}
          </span>
          <Calendar className="w-3 h-3 text-neutral-400" />
          <span className="text-xs text-neutral-500">
            {format(new Date(insight.date), 'MMM d, yyyy')}
          </span>
        </div>
        {insight.link && (
          <a
            href={insight.link}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="p-1 rounded hover:bg-neutral-100 text-neutral-400 hover:text-sourcegraph-600 transition-colors"
            title="View Source"
          >
            <ExternalLink className="w-4 h-4" />
          </a>
        )}
      </div>
      
      {/* Content */}
      <div className="p-4">
        {/* Title as clickable link */}
        <h3 className="font-semibold text-neutral-800 mb-2 line-clamp-2 group-hover:text-sourcegraph-600 transition-colors">
          <a 
            href={insight.link} 
            target="_blank" 
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="hover:text-sourcegraph-600 transition-colors"
          >
            {insight.title}
          </a>
        </h3>
        
        {/* Snippet/Summary with expand functionality */}
        <div className="text-sm text-neutral-600 leading-relaxed mb-3">
          {finalText ? (
            <p 
              className={shouldShowExpand && !isExpanded ? '' : ''}
              dangerouslySetInnerHTML={{ __html: finalText }}
            />
          ) : (
            <p className="text-neutral-500 italic">
              No preview available - click to view full article
            </p>
          )}
          {shouldShowExpand && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setIsExpanded(!isExpanded);
              }}
              className="inline-flex items-center gap-1 mt-2 text-xs text-sourcegraph-600 hover:text-sourcegraph-700 transition-colors"
            >
              {isExpanded ? (
                <>
                  <ChevronUp className="w-3 h-3" />
                  Show less
                </>
              ) : (
                <>
                  <ChevronDown className="w-3 h-3" />
                  Show more
                </>
              )}
            </button>
          )}
        </div>
        
        {/* Topics */}
        {filteredTopics && filteredTopics.length > 0 && (
          <div className="flex items-center gap-2">
            <Tag className="w-3 h-3 text-neutral-400 flex-shrink-0" />
            <div className="flex flex-wrap gap-1 min-w-0">
              {filteredTopics.slice(0, 3).map((topic, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-2 py-0.5 rounded-md text-xs bg-neutral-100 text-neutral-600 truncate"
                  title={topic}
                >
                  {topic}
                </span>
              ))}
              {filteredTopics.length > 3 && (
                <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs bg-neutral-100 text-neutral-500">
                  +{filteredTopics.length - 3}
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
