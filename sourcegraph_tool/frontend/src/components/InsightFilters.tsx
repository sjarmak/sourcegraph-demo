import { useState } from 'react';
import { Filter, X } from 'lucide-react';
import type { Insight } from '../types';

interface InsightFiltersProps {
  insights: Insight[];
  onFilterChange: (filteredInsights: Insight[]) => void;
}

export const InsightFilters = ({ insights, onFilterChange }: InsightFiltersProps) => {
  const [selectedSources, setSelectedSources] = useState<string[]>([]);
  const [isOpen, setIsOpen] = useState(false);

  // Get unique sources from insights
  const sources = Array.from(new Set(insights.map(insight => insight.tool))).sort();

  const handleSourceToggle = (source: string) => {
    const newSources = selectedSources.includes(source)
      ? selectedSources.filter(s => s !== source)
      : [...selectedSources, source];
    
    setSelectedSources(newSources);
    
    // Filter insights based on selected sources
    const filtered = newSources.length === 0 
      ? insights 
      : insights.filter(insight => newSources.includes(insight.tool));
    
    onFilterChange(filtered);
  };

  const clearFilters = () => {
    setSelectedSources([]);
    onFilterChange(insights);
  };

  const hasActiveFilters = selectedSources.length > 0;

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`inline-flex items-center px-3 py-2 border text-sm font-medium rounded-md transition-colors ${
          hasActiveFilters
            ? 'bg-sourcegraph-50 border-sourcegraph-200 text-sourcegraph-700'
            : 'bg-white border-neutral-200 text-neutral-700 hover:bg-neutral-50'
        }`}
      >
        <Filter className="w-4 h-4 mr-2" />
        Filter
        {hasActiveFilters && (
          <span className="ml-2 inline-flex items-center px-1.5 py-0.5 rounded-full text-xs bg-sourcegraph-600 text-white">
            {selectedSources.length}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-64 bg-white border border-neutral-200 rounded-lg shadow-lg z-10">
          <div className="p-3 border-b border-neutral-100">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-neutral-800">Filter by Source</h3>
              {hasActiveFilters && (
                <button
                  onClick={clearFilters}
                  className="text-xs text-neutral-500 hover:text-neutral-700 flex items-center gap-1"
                >
                  <X className="w-3 h-3" />
                  Clear
                </button>
              )}
            </div>
          </div>
          
          <div className="p-3 max-h-64 overflow-y-auto">
            <div className="space-y-2">
              {sources.map(source => (
                <label key={source} className="flex items-center text-sm">
                  <input
                    type="checkbox"
                    checked={selectedSources.includes(source)}
                    onChange={() => handleSourceToggle(source)}
                    className="w-4 h-4 text-sourcegraph-600 border-neutral-300 rounded focus:ring-sourcegraph-500 focus:ring-2"
                  />
                  <span className="ml-2 text-neutral-700 capitalize">{source}</span>
                </label>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Backdrop to close filter when clicking outside */}
      {isOpen && (
        <div
          className="fixed inset-0 z-0"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};
