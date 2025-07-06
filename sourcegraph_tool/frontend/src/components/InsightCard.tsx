import type { Insight } from '../types';
import { formatDistanceToNow } from 'date-fns';

interface InsightCardProps {
  insight: Insight;
}

export const InsightCard = ({ insight }: InsightCardProps) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
              {insight.tool}
            </span>
            <span className="text-sm text-gray-500">
              {formatDistanceToNow(new Date(insight.date), { addSuffix: true })}
            </span>
          </div>
          
          <div className="mb-3">
            <h3 className="text-lg font-semibold text-gray-900">{insight.title}</h3>
          </div>
          
          <div className="prose prose-sm max-w-none">
            <p className="text-gray-700">{insight.summary}</p>
          </div>
          
          {insight.topics && insight.topics.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1">
              {insight.topics.map((topic) => (
                <span
                  key={topic}
                  className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800"
                >
                  #{topic}
                </span>
              ))}
            </div>
          )}
          
          {insight.link && (
            <div className="mt-3">
              <a
                href={insight.link}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-primary-600 hover:text-primary-800"
              >
                View Source →
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
