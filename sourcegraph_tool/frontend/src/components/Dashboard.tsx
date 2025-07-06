import { useState, useEffect } from 'react';
import { ApiService } from '../services/api';
import { ModernInsightCard } from './ModernInsightCard';
import { StatsCard } from './StatsCard';
import { LoadingSpinner } from './LoadingSpinner';
import { ErrorMessage } from './ErrorMessage';
import type { Insight } from '../types';

export const Dashboard = () => {
  const [insights, setInsights] = useState<Insight[]>([]);
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
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Agent Insights Dashboard</h1>
          <p className="mt-2 text-gray-600">
            Track the latest developments in AI agents and coding productivity
          </p>
        </div>
        <button
          onClick={handleScrapeFeeds}
          disabled={isScrapingActive}
          className={`mt-4 lg:mt-0 inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg shadow-sm text-white transition-colors ${
            isScrapingActive
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
          }`}
        >
          {isScrapingActive ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Scraping...
            </>
          ) : (
            <>
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh Feeds
            </>
          )}
        </button>
      </div>

      {/* Stats Cards */}
      {scrapeStatus && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatsCard
            title="Total Insights (24h)"
            value={scrapeStatus.total_insights_24h}
            icon="📊"
            color="blue"
          />
          <StatsCard
            title="Active Sources"
            value={Object.keys(scrapeStatus.insights_by_tool).length}
            icon="🔗"
            color="green"
          />
          <StatsCard
            title="Last Updated"
            value={new Date(scrapeStatus.last_updated).toLocaleTimeString()}
            icon="⏰"
            color="purple"
          />
        </div>
      )}

      {/* Recent Insights */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Recent Insights</h2>
          <span className="text-sm text-gray-500">
            {insights.length} insights found
          </span>
        </div>

        {insights.length === 0 ? (
          <div className="text-center py-12 bg-gray-50 rounded-lg">
            <div className="text-gray-500">
              <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No insights yet</h3>
              <p className="text-gray-500">
                Click "Refresh Feeds" to start collecting insights from RSS feeds
              </p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {insights.map((insight) => (
              <ModernInsightCard key={insight.id} insight={insight} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
