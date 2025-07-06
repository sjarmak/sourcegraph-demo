import { format } from 'date-fns';
import type { Insight } from '../types';

interface ModernInsightCardProps {
  insight: Insight;
}

export const ModernInsightCard = ({ insight }: ModernInsightCardProps) => {
  const toolColors = {
    anthropic: 'bg-gradient-to-br from-orange-500 to-red-500',
    openai: 'bg-gradient-to-br from-green-500 to-blue-500',
    sourcegraph: 'bg-gradient-to-br from-purple-500 to-pink-500',
    github: 'bg-gradient-to-br from-gray-800 to-gray-900',
    'dev.to': 'bg-gradient-to-br from-blue-600 to-purple-600',
    hackernews: 'bg-gradient-to-br from-orange-600 to-red-600',
    aws: 'bg-gradient-to-br from-yellow-500 to-orange-500',
    google: 'bg-gradient-to-br from-blue-500 to-green-500',
    microsoft: 'bg-gradient-to-br from-blue-600 to-cyan-600',
    meta: 'bg-gradient-to-br from-blue-600 to-purple-600',
    netflix: 'bg-gradient-to-br from-red-600 to-red-700',
    uber: 'bg-gradient-to-br from-black to-gray-800',
    airbnb: 'bg-gradient-to-br from-red-500 to-pink-500',
    default: 'bg-gradient-to-br from-gray-500 to-gray-600'
  };

  const getToolColor = (tool: string) => {
    return toolColors[tool as keyof typeof toolColors] || toolColors.default;
  };

  return (
    <div className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100 group">
      {/* Header with tool badge */}
      <div className="relative p-6 pb-4">
        <div className="flex items-center justify-between mb-4">
          <div className={`inline-flex items-center px-3 py-1 rounded-full text-white text-sm font-medium ${getToolColor(insight.tool)}`}>
            <div className="w-2 h-2 bg-white rounded-full mr-2 opacity-80"></div>
            {insight.tool}
          </div>
          <span className="text-sm text-gray-500">
            {format(new Date(insight.date), 'MMM d, yyyy')}
          </span>
        </div>
        
        {/* Title */}
        <h3 className="text-xl font-bold text-gray-900 mb-3 line-clamp-2 group-hover:text-gray-700 transition-colors">
          {insight.title}
        </h3>
        
        {/* Summary */}
        <p className="text-gray-600 text-sm leading-relaxed line-clamp-3 mb-4">
          {insight.summary}
        </p>
        
        {/* Topics */}
        {insight.topics && insight.topics.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {insight.topics.slice(0, 3).map((topic, index) => (
              <span
                key={index}
                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors"
              >
                {topic}
              </span>
            ))}
            {insight.topics.length > 3 && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-500">
                +{insight.topics.length - 3} more
              </span>
            )}
          </div>
        )}
      </div>
      
      {/* Footer */}
      <div className="px-6 py-4 bg-gray-50 border-t border-gray-100">
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-500">
            Added {format(new Date(insight.created_at), 'MMM d, h:mm a')}
          </span>
          {insight.link && (
            <a
              href={insight.link}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-500 transition-colors"
            >
              View Source
              <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          )}
        </div>
      </div>
    </div>
  );
};
