import { useState, useEffect } from 'react';
import { MagnifyingGlassIcon, XMarkIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import type { InsightFilters } from '../types';
import { ApiService } from '../services/api';

interface SearchBarProps {
    filters: InsightFilters;
    onFiltersChange: (filters: InsightFilters) => void;
    onRefresh?: () => void;
    isRefreshing?: boolean;
}

interface FilterPill {
    type: 'source' | 'timeRange' | 'tag' | 'search';
    label: string;
    value: string;
    onRemove: () => void;
}

export const SearchBar = ({ filters, onFiltersChange, onRefresh, isRefreshing }: SearchBarProps) => {
    const [searchQuery, setSearchQuery] = useState(filters.q || '');
    const [sources, setSources] = useState<string[]>([]);
    const [showAdvanced, setShowAdvanced] = useState(false);

    useEffect(() => {
        const fetchSources = async () => {
            try {
                const sourcesList = await ApiService.getSources();
                setSources(sourcesList);
            } catch (error) {
                console.error('Failed to fetch sources:', error);
            }
        };

        fetchSources();
    }, []);

    const handleSearchSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onFiltersChange({
            ...filters,
            q: searchQuery || undefined,
            fromHours: undefined, // Clear time filter to search across all history
            dateRange: undefined, // Clear custom date range
        });
    };

    const handleQuickTimeFilter = (hours: number) => {
        onFiltersChange({
            ...filters,
            fromHours: hours,
            dateRange: undefined, // Clear custom date range
        });
    };

    const handleSourceToggle = (source: string) => {
        const currentSources = filters.sources || [];
        const newSources = currentSources.includes(source)
            ? currentSources.filter(s => s !== source)
            : [...currentSources, source];

        onFiltersChange({
            ...filters,
            sources: newSources.length > 0 ? newSources : undefined,
        });
    };

    const selectAllSources = () => {
        onFiltersChange({
            ...filters,
            sources: [...sources],
        });
    };

    const clearAllFilters = () => {
        setSearchQuery('');
        onFiltersChange({});
    };

    // Build filter pills
    const filterPills: FilterPill[] = [];

    if (filters.q) {
        filterPills.push({
            type: 'search',
            label: `Search: "${filters.q}"`,
            value: filters.q,
            onRemove: () => onFiltersChange({ ...filters, q: undefined })
        });
    }

    if (filters.sources?.length) {
        filters.sources.forEach(source => {
            filterPills.push({
                type: 'source',
                label: `Source: ${source}`,
                value: source,
                onRemove: () => handleSourceToggle(source)
            });
        });
    }

    if (filters.fromHours) {
        const timeLabel = filters.fromHours === 24 ? 'Last 24 hours' :
            filters.fromHours === 168 ? 'Last 7 days' :
                filters.fromHours === 720 ? 'Last 30 days' :
                    `Last ${filters.fromHours} hours`;
        filterPills.push({
            type: 'timeRange',
            label: timeLabel,
            value: filters.fromHours.toString(),
            onRemove: () => onFiltersChange({ ...filters, fromHours: undefined })
        });
    } else if (filters.dateRange?.start || filters.dateRange?.end) {
        const start = filters.dateRange?.start;
        const end = filters.dateRange?.end;
        const label = start && end ? `${start} to ${end}` :
            start ? `From ${start}` :
                `Until ${end}`;
        filterPills.push({
            type: 'timeRange',
            label: `Date: ${label}`,
            value: `${start}-${end}`,
            onRemove: () => onFiltersChange({ ...filters, dateRange: undefined })
        });
    }

    if (filters.tags?.length) {
        filters.tags.forEach(tag => {
            filterPills.push({
                type: 'tag',
                label: `Tag: ${tag}`,
                value: tag,
                onRemove: () => {
                    const newTags = filters.tags?.filter(t => t !== tag);
                    onFiltersChange({ ...filters, tags: newTags?.length ? newTags : undefined });
                }
            });
        });
    }

    return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm mb-6">
            {/* Main Search Bar */}
            <div className="p-4">
                <form onSubmit={handleSearchSubmit} className="flex gap-3">
                    <div className="flex-1 relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
                        </div>
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            placeholder="Search insights..."
                        />
                    </div>

                    <button
                        type="submit"
                        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                        Search
                    </button>

                    <button
                        type="button"
                        onClick={() => setShowAdvanced(!showAdvanced)}
                        className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                        Filters
                    </button>

                    {onRefresh && (
                        <button
                            type="button"
                            onClick={onRefresh}
                            disabled={isRefreshing}
                            className={`inline-flex items-center px-4 py-2 border text-sm font-medium rounded-md ${
                                isRefreshing
                                    ? 'bg-gray-100 border-gray-200 text-gray-400 cursor-not-allowed'
                                    : 'bg-green-600 border-green-600 text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500'
                            }`}
                        >
                            <ArrowPathIcon className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
                            {isRefreshing ? 'Refreshing...' : 'Refresh Sources'}
                        </button>
                    )}
                </form>

                {/* Quick Time Filters */}
                <div className="mt-3 flex gap-2">
                    <button
                        onClick={() => handleQuickTimeFilter(24)}
                        className={`px-3 py-1 text-xs rounded-full border ${filters.fromHours === 24
                                ? 'bg-blue-100 text-blue-800 border-blue-200'
                                : 'bg-gray-100 text-gray-700 border-gray-200 hover:bg-gray-200'
                            }`}
                    >
                        Last 24h
                    </button>
                    <button
                        onClick={() => handleQuickTimeFilter(168)}
                        className={`px-3 py-1 text-xs rounded-full border ${filters.fromHours === 168
                                ? 'bg-blue-100 text-blue-800 border-blue-200'
                                : 'bg-gray-100 text-gray-700 border-gray-200 hover:bg-gray-200'
                            }`}
                    >
                        Last 7 days
                    </button>
                    <button
                        onClick={() => handleQuickTimeFilter(720)}
                        className={`px-3 py-1 text-xs rounded-full border ${filters.fromHours === 720
                                ? 'bg-blue-100 text-blue-800 border-blue-200'
                                : 'bg-gray-100 text-gray-700 border-gray-200 hover:bg-gray-200'
                            }`}
                    >
                        Last 30 days
                    </button>
                </div>
            </div>

            {/* Advanced Filters */}
            {showAdvanced && (
                <div className="border-t border-gray-200 p-4 bg-gray-50">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Source Filter */}
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <label className="block text-sm font-medium text-gray-700">
                                    {filters.sources?.length ? `Limited to ${filters.sources.length} source${filters.sources.length === 1 ? '' : 's'}` : 'Search all sources'}
                                </label>
                                <div className="flex gap-2">
                                    {!filters.sources?.length && (
                                        <button
                                            type="button"
                                            onClick={selectAllSources}
                                            className="text-xs text-blue-600 hover:text-blue-700"
                                        >
                                            Select All
                                        </button>
                                    )}
                                    {filters.sources?.length && (
                                        <button
                                            type="button"
                                            onClick={() => onFiltersChange({ ...filters, sources: undefined })}
                                            className="text-xs text-gray-500 hover:text-gray-700"
                                        >
                                            Clear
                                        </button>
                                    )}
                                </div>
                            </div>
                            <p className="text-xs text-gray-500 mb-2">
                                {filters.sources?.length ? 'Results limited to selected sources' : 'Default: searches across all available sources'}
                            </p>
                            <div className="space-y-2 max-h-32 overflow-y-auto">
                                {sources.map((source) => (
                                    <label key={source} className="flex items-center">
                                        <input
                                            type="checkbox"
                                            checked={filters.sources?.includes(source) || false}
                                            onChange={() => handleSourceToggle(source)}
                                            className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                                        />
                                        <span className="ml-2 text-sm text-gray-700 capitalize">{source.replace(/_/g, ' ')}</span>
                                    </label>
                                ))}
                            </div>
                        </div>

                        {/* Custom Date Range */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Custom Date Range
                            </label>
                            <div className="space-y-2">
                                <input
                                    type="date"
                                    value={filters.dateRange?.start || ''}
                                    onChange={(e) => onFiltersChange({
                                        ...filters,
                                        dateRange: {
                                            start: e.target.value,
                                            end: filters.dateRange?.end || ''
                                        },
                                        fromHours: undefined // Clear quick filters
                                    })}
                                    className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                    placeholder="From date"
                                />
                                <input
                                    type="date"
                                    value={filters.dateRange?.end || ''}
                                    onChange={(e) => onFiltersChange({
                                        ...filters,
                                        dateRange: {
                                            start: filters.dateRange?.start || '',
                                            end: e.target.value
                                        },
                                        fromHours: undefined // Clear quick filters
                                    })}
                                    className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                    placeholder="To date"
                                />
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Active Filter Pills */}
            {filterPills.length > 0 && (
                <div className="border-t border-gray-200 p-4">
                    <div className="flex flex-wrap gap-2 items-center">
                        <span className="text-sm text-gray-600 font-medium">Active filters:</span>
                        {filterPills.map((pill, index) => (
                            <span
                                key={index}
                                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                            >
                                {pill.label}
                                <button
                                    type="button"
                                    onClick={pill.onRemove}
                                    className="ml-1.5 inline-flex items-center justify-center h-4 w-4 rounded-full text-blue-400 hover:bg-blue-200 hover:text-blue-500 focus:outline-none focus:bg-blue-500 focus:text-white"
                                >
                                    <XMarkIcon className="h-3 w-3" />
                                </button>
                            </span>
                        ))}
                        <button
                            onClick={clearAllFilters}
                            className="text-xs text-gray-500 hover:text-gray-700 underline ml-2"
                        >
                            Clear all
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};
