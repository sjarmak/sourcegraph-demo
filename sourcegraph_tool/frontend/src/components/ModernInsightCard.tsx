import { formatDistanceToNow } from 'date-fns';
import { ExternalLink, Calendar, Tag } from 'lucide-react';
import type { Insight } from '../types';

interface ModernInsightCardProps {
  insight: Insight;
}

export const ModernInsightCard = ({ insight }: ModernInsightCardProps) => {
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

  return (
    <div className="bg-white border border-neutral-200 rounded-lg hover:bg-neutral-50 hover:border-neutral-300 transition-all duration-200 cursor-pointer group">
      {/* Header bar */}
      <div className="flex items-center justify-between p-4 pb-3 border-b border-neutral-100">
        <div className="flex items-center gap-2">
          <span className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium border ${getSourceColor(insight.tool)}`}>
            {insight.tool.replace(/_/g, ' ').replace(/([A-Z])/g, ' $1').trim()}
          </span>
          <Calendar className="w-3 h-3 text-neutral-400" />
          <span className="text-xs text-neutral-500">
            {formatDistanceToNow(new Date(insight.date), { addSuffix: true })}
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
        {/* Title */}
        <h3 className="font-semibold text-neutral-800 mb-2 line-clamp-2 group-hover:text-sourcegraph-600 transition-colors">
          {insight.title}
        </h3>
        
        {/* Summary */}
        <p className="text-sm text-neutral-600 leading-relaxed line-clamp-3 mb-3">
          {insight.summary?.replace(/<[^>]*>/g, '') || ''}
        </p>
        
        {/* Topics */}
        {insight.topics && insight.topics.length > 0 && (
          <div className="flex items-center gap-2">
            <Tag className="w-3 h-3 text-neutral-400 flex-shrink-0" />
            <div className="flex flex-wrap gap-1 min-w-0">
              {insight.topics.slice(0, 3).map((topic, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-2 py-0.5 rounded-md text-xs bg-neutral-100 text-neutral-600 truncate"
                  title={topic}
                >
                  {topic}
                </span>
              ))}
              {insight.topics.length > 3 && (
                <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs bg-neutral-100 text-neutral-500">
                  +{insight.topics.length - 3}
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
