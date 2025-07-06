import { useState } from 'react';
import { ModernInsightCard } from '../components/ModernInsightCard';
import { Filters } from '../components/Filters';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage';
import { useInsights } from '../hooks/useInsights';
import type { InsightFilters } from '../types';

export const Insights = () => {
  const [filters, setFilters] = useState<InsightFilters>({});
  const { insights, loading, error } = useInsights(filters);

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  return (
    <div className="px-4 sm:px-0">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Insights</h1>
        <p className="mt-1 text-sm text-gray-600">
          Track and analyze agentic insights across your tools
        </p>
      </div>

      <Filters filters={filters} onFiltersChange={setFilters} />

      <div className="mb-4 text-sm text-gray-600">
        {insights.length} insight{insights.length !== 1 ? 's' : ''} found
      </div>

      {insights.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-500">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No insights found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Try adjusting your filters or check back later for new insights.
            </p>
          </div>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {insights.map((insight) => (
            <ModernInsightCard key={insight.id} insight={insight} />
          ))}
        </div>
      )}
    </div>
  );
};
