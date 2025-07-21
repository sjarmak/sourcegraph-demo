import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { ModernInsightCard } from '../components/ModernInsightCard';
import { SearchBar } from '../components/SearchBar';

import { LoadingSkeleton } from '../components/LoadingSkeleton';
import { ErrorMessage } from '../components/ErrorMessage';
import { useInsights } from '../hooks/useInsights';
import { ApiService } from '../services/api';
import type { InsightFilters } from '../types';

export const Insights = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  
  // Initialize filters from URL params or defaults
  const [filters, setFilters] = useState<InsightFilters>(() => {
    const urlFilters: InsightFilters = {};
    
    if (searchParams.get('q')) urlFilters.q = searchParams.get('q')!;
    if (searchParams.get('sources')) urlFilters.sources = searchParams.get('sources')!.split(',');
    if (searchParams.get('fromHours')) urlFilters.fromHours = parseInt(searchParams.get('fromHours')!);
    if (searchParams.get('dateFrom') && searchParams.get('dateTo')) {
      urlFilters.dateRange = {
        start: searchParams.get('dateFrom')!,
        end: searchParams.get('dateTo')!
      };
    }
    if (searchParams.get('tags')) urlFilters.tags = searchParams.get('tags')!.split(',');
    
    return {
      fromHours: 720, // Default to last 30 days (24 * 30)
      // Remove limit to show all records by default
      ...urlFilters
    };
  });

  const { insights, loading, error, refetch } = useInsights(filters);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [displayCount, setDisplayCount] = useState(20);

  // Update URL when filters change
  useEffect(() => {
    const params = new URLSearchParams();
    
    if (filters.q) params.set('q', filters.q);
    if (filters.sources?.length) params.set('sources', filters.sources.join(','));
    if (filters.fromHours) params.set('fromHours', filters.fromHours.toString());
    if (filters.dateRange?.start) params.set('dateFrom', filters.dateRange.start);
    if (filters.dateRange?.end) params.set('dateTo', filters.dateRange.end);
    if (filters.tags?.length) params.set('tags', filters.tags.join(','));
    
    setSearchParams(params, { replace: true });
  }, [filters, setSearchParams]);

  const handleRefreshSources = async () => {
    try {
      setIsRefreshing(true);
      await ApiService.scrapeFeeds();
      
      // Wait a moment then refetch insights
      setTimeout(async () => {
        await refetch();
        setIsRefreshing(false);
      }, 3000);
    } catch (error) {
      console.error('Failed to refresh sources:', error);
      setIsRefreshing(false);
    }
  };

  if (error) {
    return <ErrorMessage message={error} />;
  }

  return (
    <div className="px-4 sm:px-0">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Agentic Insight Tracker</h1>
        <p className="mt-1 text-sm text-gray-600">
          Monitor developments in AI coding agents across multiple sources
        </p>
      </div>

      <SearchBar 
        filters={filters} 
        onFiltersChange={setFilters} 
        onRefresh={handleRefreshSources}
        isRefreshing={isRefreshing}
      />

      <div className="mb-4 flex items-center justify-between">
        <div className="text-sm text-gray-600">
          {insights.length} insight{insights.length !== 1 ? 's' : ''} found (showing {Math.min(displayCount, insights.length)} of {insights.length})
        </div>
        {filters.fromHours && (
          <div className="text-xs text-gray-500">
            Showing insights from the last {filters.fromHours === 24 ? '24 hours' : 
              filters.fromHours === 168 ? '7 days' : 
              filters.fromHours === 720 ? '30 days' : 
              filters.fromHours === 2160 ? '3 months' :
              filters.fromHours === 4320 ? '6 months' :
              filters.fromHours === 6480 ? '9 months' :
              filters.fromHours === 8760 ? '1 year' :
              `${filters.fromHours} hours`}
          </div>
        )}
      </div>

      <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Insights</h2>

      {loading ? (
        <LoadingSkeleton />
      ) : insights.length === 0 ? (
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
        <>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {insights.slice(0, displayCount).map((insight) => (
              <ModernInsightCard key={insight.id} insight={insight} searchQuery={filters.q} />
            ))}
          </div>
          
          {displayCount < insights.length && (
            <div className="text-center mt-8">
              <button
                onClick={() => setDisplayCount(prev => Math.min(prev + 20, insights.length))}
                className="inline-flex items-center px-6 py-3 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sourcegraph-500 transition-colors"
              >
                Show More ({Math.min(20, insights.length - displayCount)} more)
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};
