import { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  type ChartOptions,
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';
import { ApiService } from '../services/api';
import type { TrendData } from '../types';
import { format, parseISO } from 'date-fns';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
);

export const Trends = () => {
  const [trendData, setTrendData] = useState<TrendData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [period, setPeriod] = useState('7d');
  const [chartType, setChartType] = useState<'bar' | 'line'>('bar');

  useEffect(() => {
    const fetchTrends = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const data = await ApiService.getTrends(period);
        setTrendData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchTrends();
  }, [period]);

  const prepareChartData = () => {
    if (!trendData.length) return null;

    // Group data by date
    const dateGroups = trendData.reduce((acc, item) => {
      const date = format(parseISO(item.date), 'MMM dd');
      if (!acc[date]) {
        acc[date] = {};
      }
      acc[date][item.tool] = item.count;
      return acc;
    }, {} as Record<string, Record<string, number>>);

    // Get unique tools
    const tools = [...new Set(trendData.map(item => item.tool))];
    const dates = Object.keys(dateGroups).sort();

    // Create datasets for each tool
    const datasets = tools.map((tool, index) => ({
      label: tool,
      data: dates.map(date => dateGroups[date][tool] || 0),
      backgroundColor: `hsla(${(index * 360 / tools.length) % 360}, 70%, 50%, 0.6)`,
      borderColor: `hsla(${(index * 360 / tools.length) % 360}, 70%, 50%, 1)`,
      borderWidth: 2,
    }));

    return {
      labels: dates,
      datasets,
    };
  };

  const chartOptions: ChartOptions<'bar' | 'line'> = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Insight Frequency by Tool Over Time',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1,
        },
      },
    },
  };

  const chartData = prepareChartData();

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">
              Error loading trends
            </h3>
            <p className="mt-1 text-sm text-red-700">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 sm:px-0">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Trends</h1>
        <p className="mt-1 text-sm text-gray-600">
          Analyze insight frequency patterns across tools and time
        </p>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex flex-wrap gap-4 items-center">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Time Period
            </label>
            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
              className="rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Chart Type
            </label>
            <select
              value={chartType}
              onChange={(e) => setChartType(e.target.value as 'bar' | 'line')}
              className="rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            >
              <option value="bar">Bar Chart</option>
              <option value="line">Line Chart</option>
            </select>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        {chartData && chartData.datasets.length > 0 ? (
          <div className="h-96">
            {chartType === 'bar' ? (
              <Bar data={chartData} options={chartOptions} />
            ) : (
              <Line data={chartData} options={chartOptions} />
            )}
          </div>
        ) : (
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
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No trend data available</h3>
              <p className="mt-1 text-sm text-gray-500">
                Check back later or adjust your time period.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Summary Stats */}
      {trendData.length > 0 && (
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900">Total Insights</h3>
            <p className="text-3xl font-bold text-primary-600">
              {trendData.reduce((sum, item) => sum + item.count, 0)}
            </p>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900">Active Tools</h3>
            <p className="text-3xl font-bold text-primary-600">
              {new Set(trendData.map(item => item.tool)).size}
            </p>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900">Avg per Day</h3>
            <p className="text-3xl font-bold text-primary-600">
              {Math.round(trendData.reduce((sum, item) => sum + item.count, 0) / 
                new Set(trendData.map(item => item.date)).size)}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
