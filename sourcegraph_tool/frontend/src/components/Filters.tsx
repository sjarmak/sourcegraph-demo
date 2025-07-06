import { useState, useEffect } from 'react';
import type { InsightFilters } from '../types';
import { ApiService } from '../services/api';

interface FiltersProps {
  filters: InsightFilters;
  onFiltersChange: (filters: InsightFilters) => void;
}

export const Filters = ({ filters, onFiltersChange }: FiltersProps) => {
  const [tools, setTools] = useState<string[]>([]);
  const [keyword, setKeyword] = useState(filters.keyword || '');

  useEffect(() => {
    const fetchTools = async () => {
      try {
        const toolsList = await ApiService.getTools();
        setTools(toolsList);
      } catch (error) {
        console.error('Failed to fetch tools:', error);
      }
    };
    
    fetchTools();
  }, []);

  const handleToolChange = (tool: string) => {
    onFiltersChange({
      ...filters,
      tool: tool === 'all' ? undefined : tool,
    });
  };

  const handleKeywordChange = (value: string) => {
    setKeyword(value);
  };

  const handleKeywordSubmit = () => {
    onFiltersChange({
      ...filters,
      keyword: keyword || undefined,
    });
  };

  const handleDateRangeChange = (field: 'start' | 'end', value: string) => {
    onFiltersChange({
      ...filters,
      dateRange: {
        start: filters.dateRange?.start || '',
        end: filters.dateRange?.end || '',
        [field]: value,
      },
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Search */}
        <div className="md:col-span-2">
          <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-1">
            Search
          </label>
          <div className="flex">
            <input
              type="text"
              id="search"
              value={keyword}
              onChange={(e) => handleKeywordChange(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleKeywordSubmit()}
              className="flex-1 rounded-l-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
              placeholder="Search insights..."
            />
            <button
              onClick={handleKeywordSubmit}
              className="px-4 py-2 bg-primary-600 text-white rounded-r-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
            >
              Search
            </button>
          </div>
        </div>

        {/* Tool Filter */}
        <div>
          <label htmlFor="tool" className="block text-sm font-medium text-gray-700 mb-1">
            Tool
          </label>
          <select
            id="tool"
            value={filters.tool || 'all'}
            onChange={(e) => handleToolChange(e.target.value)}
            className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          >
            <option value="all">All Tools</option>
            {tools.map((tool) => (
              <option key={tool} value={tool}>
                {tool}
              </option>
            ))}
          </select>
        </div>

        {/* Date Range */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Date Range
          </label>
          <div className="space-y-2">
            <input
              type="date"
              value={filters.dateRange?.start || ''}
              onChange={(e) => handleDateRangeChange('start', e.target.value)}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            />
            <input
              type="date"
              value={filters.dateRange?.end || ''}
              onChange={(e) => handleDateRangeChange('end', e.target.value)}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            />
          </div>
        </div>
      </div>

      {/* Clear Filters */}
      {(filters.tool || filters.keyword || filters.dateRange?.start || filters.dateRange?.end) && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <button
            onClick={() => onFiltersChange({})}
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            Clear all filters
          </button>
        </div>
      )}
    </div>
  );
};
