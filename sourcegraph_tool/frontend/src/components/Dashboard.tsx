import { useState, useEffect } from 'react';
import { RefreshCw, BarChart3, Link, Clock } from 'lucide-react';
import { ApiService } from '../services/api';
import { ModernInsightCard } from './ModernInsightCard';
import { InsightFilters } from './InsightFilters';
import { LoadingSpinner } from './LoadingSpinner';
import { ErrorMessage } from './ErrorMessage';
import type { Insight } from '../types';

export const Dashboard = () => {
  const [insights, setInsights] = useState<Insight[]>([]);
  const [filteredInsights, setFilteredInsights] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [scrapeStatus, setScrapeStatus] = useState<any>(null);
  const [isScrapingActive, setIsScrapingActive] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [insightsData, statusData] = await Promise.all([
        ApiService.getInsights({ limit: 50 }),
        ApiService.getScrapeStatus()
      ]);
      
      setInsights(insightsData);
      setFilteredInsights(insightsData);
      setScrapeStatus(statusData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleScrapeFeeds = async () => {
    try {
      setIsScrapingActive(true);
      await ApiService.scrapeFeeds();
      
      // Poll for updates
      const pollInterval = setInterval(async () => {
        try {
          const status = await ApiService.getScrapeStatus();
          setScrapeStatus(status);
          
          // Refresh insights after scraping
          const newInsights = await ApiService.getInsights({ limit: 50 });
          setInsights(newInsights);
          setFilteredInsights(newInsights);
        } catch (err) {
          clearInterval(pollInterval);
        }
      }, 5000);
      
      // Stop polling after 30 seconds
      setTimeout(() => {
        clearInterval(pollInterval);
        setIsScrapingActive(false);
      }, 30000);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start scraping');
      setIsScrapingActive(false);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorMessage message={error} onRetry={fetchDashboardData} />;
  }

  return (
    <div className="space-y-6">
      {/* Compact Header with Inline Metrics */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="flex items-center gap-6">
          <div>
            <h1 className="text-2xl font-semibold text-neutral-800">Agent Insights Dashboard</h1>
            <p className="text-sm text-neutral-500 mt-1">
              Track the latest developments in AI agents and coding productivity
            </p>
          </div>
          
          {/* Inline Stats */}
          {scrapeStatus && (
            <div className="hidden lg:flex items-center gap-6 text-sm">
              <div className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-neutral-400" />
                <span className="font-medium text-neutral-700">{scrapeStatus.total_insights_24h}</span>
                <span className="text-neutral-500">insights (24h)</span>
              </div>
              <div className="flex items-center gap-2">
                <Link className="w-4 h-4 text-neutral-400" />
                <span className="font-medium text-neutral-700">{Object.keys(scrapeStatus.insights_by_tool).length}</span>
                <span className="text-neutral-500">sources</span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-neutral-400" />
                <span className="text-neutral-500">updated {new Date(scrapeStatus.last_updated).toLocaleTimeString()}</span>
              </div>
            </div>
          )}
        </div>
        
        <button
          onClick={handleScrapeFeeds}
          disabled={isScrapingActive}
          className={`inline-flex items-center px-4 py-2 border text-sm font-medium rounded-md transition-colors ${
            isScrapingActive
              ? 'bg-neutral-100 border-neutral-200 text-neutral-400 cursor-not-allowed'
              : 'bg-sourcegraph-600 border-sourcegraph-600 text-white hover:bg-sourcegraph-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sourcegraph-500'
          }`}
        >
          {isScrapingActive ? (
            <>
              <RefreshCw className="animate-spin w-4 h-4 mr-2" />
              Refreshing...
            </>
          ) : (
            <>
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh Feeds
            </>
          )}
        </button>
      </div>

      {/* Mobile Stats */}
      {scrapeStatus && (
        <div className="lg:hidden grid grid-cols-3 gap-4 p-4 bg-neutral-50 rounded-lg border border-neutral-200">
          <div className="text-center">
            <div className="font-semibold text-neutral-800">{scrapeStatus.total_insights_24h}</div>
            <div className="text-xs text-neutral-500">insights (24h)</div>
          </div>
          <div className="text-center">
            <div className="font-semibold text-neutral-800">{Object.keys(scrapeStatus.insights_by_tool).length}</div>
            <div className="text-xs text-neutral-500">sources</div>
          </div>
          <div className="text-center">
            <div className="text-xs text-neutral-800">{new Date(scrapeStatus.last_updated).toLocaleTimeString()}</div>
            <div className="text-xs text-neutral-500">last updated</div>
          </div>
        </div>
      )}

      {/* Recent Insights */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-neutral-800">Recent Insights</h2>
          <div className="flex items-center gap-4">
            <InsightFilters insights={insights} onFilterChange={setFilteredInsights} />
            <span className="text-sm text-neutral-500">
              {filteredInsights.length} of {insights.length} shown
            </span>
          </div>
        </div>

        {filteredInsights.length === 0 ? (
          <div className="text-center py-16 bg-neutral-50 rounded-lg border border-neutral-200">
            <div className="text-neutral-500">
              <BarChart3 className="mx-auto h-8 w-8 text-neutral-300 mb-3" />
              <h3 className="text-base font-medium text-neutral-700 mb-2">No insights yet</h3>
              <p className="text-sm text-neutral-500">
                Click "Refresh Feeds" to start collecting insights
              </p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredInsights.map((insight) => (
              <ModernInsightCard key={insight.id} insight={insight} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
