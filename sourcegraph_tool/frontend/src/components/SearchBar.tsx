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
    type: 'source' | 'timeRange' | 'tag' | 'search' | 'tool' | 'keyword';
    label: string;
    value: string;
    onRemove: () => void;
}

export const SearchBar = ({ filters, onFiltersChange, onRefresh, isRefreshing }: SearchBarProps) => {
    const [searchQuery, setSearchQuery] = useState(filters.q || '');
    const [sources, setSources] = useState<string[]>([]);
    const [mentionedTools, setMentionedTools] = useState<string[]>([]);
    const [matchedKeywords, setMatchedKeywords] = useState<string[]>([]);
    const [showAdvanced, setShowAdvanced] = useState(false);

    useEffect(() => {
        const fetchFilterOptions = async () => {
            try {
                const [sourcesList, toolsList, keywordsList] = await Promise.all([
                    ApiService.getSources(),
                    ApiService.getMentionedTools(),
                    ApiService.getMatchedKeywords()
                ]);
                setSources(sourcesList);
                setMentionedTools(toolsList);
                setMatchedKeywords(keywordsList);
            } catch (error) {
                console.error('Failed to fetch filter options:', error);
            }
        };

        fetchFilterOptions();
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

    const handleToolToggle = (tool: string) => {
        const currentTools = filters.mentioned_tools || [];
        const newTools = currentTools.includes(tool)
            ? currentTools.filter(t => t !== tool)
            : [...currentTools, tool];

        onFiltersChange({
            ...filters,
            mentioned_tools: newTools.length > 0 ? newTools : undefined,
        });
    };

    const handleKeywordToggle = (keyword: string) => {
        const currentKeywords = filters.matched_keywords || [];
        const newKeywords = currentKeywords.includes(keyword)
            ? currentKeywords.filter(k => k !== keyword)
            : [...currentKeywords, keyword];

        onFiltersChange({
            ...filters,
            matched_keywords: newKeywords.length > 0 ? newKeywords : undefined,
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

    if (filters.mentioned_tools?.length) {
        filters.mentioned_tools.forEach(tool => {
            filterPills.push({
                type: 'tool',
                label: `Tool: ${tool}`,
                value: tool,
                onRemove: () => handleToolToggle(tool)
            });
        });
    }

    if (filters.matched_keywords?.length) {
        filters.matched_keywords.forEach(keyword => {
            filterPills.push({
                type: 'keyword',
                label: `Keyword: ${keyword}`,
                value: keyword,
                onRemove: () => handleKeywordToggle(keyword)
            });
        });
    }

    if (filters.fromHours) {
        const timeLabel = filters.fromHours === 24 ? 'Last 24 hours' :
            filters.fromHours === 168 ? 'Last 7 days' :
                filters.fromHours === 720 ? 'Last 30 days' :
                    filters.fromHours === 2160 ? 'Last 3 months' :
                        filters.fromHours === 4320 ? 'Last 6 months' :
                            filters.fromHours === 6480 ? 'Last 9 months' :
                                filters.fromHours === 8760 ? 'Last 1 year' :
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
                <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row gap-3">
                    <div className="flex-1 relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
                        </div>
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="block w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm touch-manipulation"
                            placeholder="Search insights..."
                        />
                    </div>

                    <div className="flex flex-col sm:flex-row gap-3">
                        <button
                            type="submit"
                            className="inline-flex items-center justify-center px-4 py-2.5 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 active:bg-blue-800 touch-manipulation w-full sm:w-auto"
                        >
                            Search
                        </button>

                        <button
                            type="button"
                            onClick={() => setShowAdvanced(!showAdvanced)}
                            className="inline-flex items-center justify-center px-4 py-2.5 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 active:bg-gray-100 touch-manipulation w-full sm:w-auto"
                        >
                            Filters
                        </button>

                        {onRefresh && (
                            <button
                                type="button"
                                onClick={onRefresh}
                                disabled={isRefreshing}
                                className={`inline-flex items-center justify-center px-4 py-2.5 border text-sm font-medium rounded-md touch-manipulation w-full sm:w-auto ${
                                    isRefreshing
                                        ? 'bg-gray-100 border-gray-200 text-gray-400 cursor-not-allowed'
                                        : 'bg-green-600 border-green-600 text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 active:bg-green-800'
                                }`}
                            >
                                <ArrowPathIcon className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
                                {isRefreshing ? 'Refreshing...' : 'Refresh Sources'}
                            </button>
                        )}
                    </div>
                </form>

                {/* Quick Time Filters */}
                <div className="mt-3 flex flex-wrap gap-2">
                    <button
                        onClick={() => handleQuickTimeFilter(24)}
                        className={`px-4 py-2 text-sm rounded-full border touch-manipulation ${filters.fromHours === 24
                                ? 'bg-blue-100 text-blue-800 border-blue-200'
                                : 'bg-gray-100 text-gray-700 border-gray-200 hover:bg-gray-200 active:bg-gray-300'
                            }`}
                    >
                        Last 24h
                    </button>
                    <button
                        onClick={() => handleQuickTimeFilter(168)}
                        className={`px-4 py-2 text-sm rounded-full border touch-manipulation ${filters.fromHours === 168
                                ? 'bg-blue-100 text-blue-800 border-blue-200'
                                : 'bg-gray-100 text-gray-700 border-gray-200 hover:bg-gray-200 active:bg-gray-300'
                            }`}
                    >
                        Last 7 days
                    </button>
                    <button
                        onClick={() => handleQuickTimeFilter(720)}
                        className={`px-4 py-2 text-sm rounded-full border touch-manipulation ${filters.fromHours === 720
                                ? 'bg-blue-100 text-blue-800 border-blue-200'
                                : 'bg-gray-100 text-gray-700 border-gray-200 hover:bg-gray-200 active:bg-gray-300'
                            }`}
                    >
                        Last 30 days
                    </button>
                    <button
                        onClick={() => handleQuickTimeFilter(2160)}
                        className={`px-4 py-2 text-sm rounded-full border touch-manipulation ${filters.fromHours === 2160
                                ? 'bg-blue-100 text-blue-800 border-blue-200'
                                : 'bg-gray-100 text-gray-700 border-gray-200 hover:bg-gray-200 active:bg-gray-300'
                            }`}
                    >
                        Last 3 months
                    </button>
                    <button
                        onClick={() => handleQuickTimeFilter(4320)}
                        className={`px-4 py-2 text-sm rounded-full border touch-manipulation ${filters.fromHours === 4320
                                ? 'bg-blue-100 text-blue-800 border-blue-200'
                                : 'bg-gray-100 text-gray-700 border-gray-200 hover:bg-gray-200 active:bg-gray-300'
                            }`}
                    >
                        Last 6 months
                    </button>
                    <button
                        onClick={() => handleQuickTimeFilter(6480)}
                        className={`px-4 py-2 text-sm rounded-full border touch-manipulation ${filters.fromHours === 6480
                                ? 'bg-blue-100 text-blue-800 border-blue-200'
                                : 'bg-gray-100 text-gray-700 border-gray-200 hover:bg-gray-200 active:bg-gray-300'
                            }`}
                    >
                        Last 9 months
                    </button>
                    <button
                        onClick={() => handleQuickTimeFilter(8760)}
                        className={`px-4 py-2 text-sm rounded-full border touch-manipulation ${filters.fromHours === 8760
                                ? 'bg-blue-100 text-blue-800 border-blue-200'
                                : 'bg-gray-100 text-gray-700 border-gray-200 hover:bg-gray-200 active:bg-gray-300'
                            }`}
                    >
                        Last 1 year
                        </button>
                        </div>

                 {/* Quick Coding Agent Filters */}
                 <div className="mt-3">
                     <label className="block text-sm font-medium text-gray-700 mb-2">
                         Filter by AI Coding Tools
                     </label>
                     <div className="flex flex-wrap gap-2">
                         {['Amp', 'Cursor', 'GitHub Copilot', 'Claude', 'Cody'].map((tool) => (
                             <button
                                 key={tool}
                                 onClick={() => handleToolToggle(tool)}
                                 className={`px-3 py-1.5 text-sm rounded-full border touch-manipulation ${
                                     filters.mentioned_tools?.includes(tool)
                                         ? 'bg-purple-100 text-purple-800 border-purple-200'
                                         : 'bg-gray-100 text-gray-700 border-gray-200 hover:bg-gray-200 active:bg-gray-300'
                                 }`}
                             >
                                 {tool}
                             </button>
                         ))}
                         <button
                             onClick={() => setShowAdvanced(!showAdvanced)}
                             className="px-3 py-1.5 text-sm rounded-full border border-gray-300 text-gray-600 hover:bg-gray-50 touch-manipulation"
                         >
                             More Tools...
                         </button>
                     </div>
                 </div>
             </div>

            {/* Advanced Filters */}
            {showAdvanced && (
                <div className="border-t border-gray-200 p-4 bg-gray-50 sm:block hidden">
                    <div className="grid grid-cols-1 lg:grid-cols-3 md:grid-cols-2 gap-4">
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
                                            className="text-xs text-blue-600 hover:text-blue-700 py-1 px-2 touch-manipulation"
                                        >
                                            Select All
                                        </button>
                                    )}
                                    {filters.sources?.length && (
                                        <button
                                            type="button"
                                            onClick={() => onFiltersChange({ ...filters, sources: undefined })}
                                            className="text-xs text-gray-500 hover:text-gray-700 py-1 px-2 touch-manipulation"
                                        >
                                            Clear
                                        </button>
                                    )}
                                </div>
                            </div>
                            <p className="text-xs text-gray-500 mb-2">
                                {filters.sources?.length ? 'Results limited to selected sources' : 'Default: searches across all available sources'}
                            </p>
                            <div className="space-y-3 max-h-32 overflow-y-auto">
                                {sources.map((source) => (
                                    <label key={source} className="flex items-center cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={filters.sources?.includes(source) || false}
                                            onChange={() => handleSourceToggle(source)}
                                            className="h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500 touch-manipulation"
                                        />
                                        <span className="ml-3 text-sm text-gray-700 capitalize select-none">{source.replace(/_/g, ' ')}</span>
                                    </label>
                                ))}
                            </div>
                        </div>

                        {/* Custom Date Range */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Custom Date Range
                            </label>
                            <div className="space-y-3">
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
                                    className="w-full py-2.5 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm touch-manipulation"
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
                                    className="w-full py-2.5 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm touch-manipulation"
                                    placeholder="To date"
                                    />
                                    </div>
                                    </div>

                        {/* Mentioned Tools Filter */}
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <label className="block text-sm font-medium text-gray-700">
                                    {filters.mentioned_tools?.length ? `${filters.mentioned_tools.length} tool${filters.mentioned_tools.length === 1 ? '' : 's'} selected` : 'All AI coding tools'}
                                </label>
                                {filters.mentioned_tools?.length && (
                                    <button
                                        type="button"
                                        onClick={() => onFiltersChange({ ...filters, mentioned_tools: undefined })}
                                        className="text-xs text-gray-500 hover:text-gray-700 py-1 px-2 touch-manipulation"
                                    >
                                        Clear
                                    </button>
                                )}
                            </div>
                            <p className="text-xs text-gray-500 mb-2">
                                Filter by AI coding tools mentioned in content
                            </p>
                            <div className="space-y-3 max-h-32 overflow-y-auto">
                                {mentionedTools.map((tool) => (
                                    <label key={tool} className="flex items-center cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={filters.mentioned_tools?.includes(tool) || false}
                                            onChange={() => handleToolToggle(tool)}
                                            className="h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500 touch-manipulation"
                                        />
                                        <span className="ml-3 text-sm text-gray-700 select-none">{tool}</span>
                                    </label>
                                ))}
                            </div>
                        </div>

                        {/* Matched Keywords Filter */}
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <label className="block text-sm font-medium text-gray-700">
                                    {filters.matched_keywords?.length ? `${filters.matched_keywords.length} keyword${filters.matched_keywords.length === 1 ? '' : 's'} selected` : 'All matched keywords'}
                                </label>
                                {filters.matched_keywords?.length && (
                                    <button
                                        type="button"
                                        onClick={() => onFiltersChange({ ...filters, matched_keywords: undefined })}
                                        className="text-xs text-gray-500 hover:text-gray-700 py-1 px-2 touch-manipulation"
                                    >
                                        Clear
                                    </button>
                                )}
                            </div>
                            <p className="text-xs text-gray-500 mb-2">
                                Filter by RSS feed keywords that matched content
                            </p>
                            <div className="space-y-3 max-h-32 overflow-y-auto">
                                {matchedKeywords.map((keyword) => (
                                    <label key={keyword} className="flex items-center cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={filters.matched_keywords?.includes(keyword) || false}
                                            onChange={() => handleKeywordToggle(keyword)}
                                            className="h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500 touch-manipulation"
                                        />
                                        <span className="ml-3 text-sm text-gray-700 select-none">{keyword}</span>
                                    </label>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Mobile-only bottom sheet for advanced filters */}
            {showAdvanced && (
                <div className="sm:hidden fixed inset-0 z-50 bg-white flex flex-col">
                    <div className="flex items-center justify-between p-4 border-b border-gray-200">
                        <h2 className="text-lg font-semibold text-gray-900">Filters</h2>
                        <button
                            onClick={() => setShowAdvanced(false)}
                            className="p-2 text-gray-400 hover:text-gray-600 touch-manipulation"
                        >
                            <XMarkIcon className="h-6 w-6" />
                        </button>
                    </div>
                    
                    <div className="flex-1 overflow-y-auto p-4 space-y-6">
                        {/* Source Filter */}
                        <div>
                            <div className="flex items-center justify-between mb-3">
                                <label className="block text-base font-medium text-gray-700">
                                    Sources
                                </label>
                                <div className="flex gap-3">
                                    {!filters.sources?.length && (
                                        <button
                                            type="button"
                                            onClick={selectAllSources}
                                            className="text-sm text-blue-600 hover:text-blue-700 py-2 px-3 touch-manipulation"
                                        >
                                            Select All
                                        </button>
                                    )}
                                    {filters.sources?.length && (
                                        <button
                                            type="button"
                                            onClick={() => onFiltersChange({ ...filters, sources: undefined })}
                                            className="text-sm text-gray-500 hover:text-gray-700 py-2 px-3 touch-manipulation"
                                        >
                                            Clear
                                        </button>
                                    )}
                                </div>
                            </div>
                            <p className="text-sm text-gray-500 mb-4">
                                {filters.sources?.length ? `Limited to ${filters.sources.length} selected source${filters.sources.length === 1 ? '' : 's'}` : 'Search across all available sources'}
                            </p>
                            <div className="space-y-4">
                                {sources.map((source) => (
                                    <label key={source} className="flex items-center cursor-pointer py-2">
                                        <input
                                            type="checkbox"
                                            checked={filters.sources?.includes(source) || false}
                                            onChange={() => handleSourceToggle(source)}
                                            className="h-6 w-6 text-blue-600 border-gray-300 rounded focus:ring-blue-500 touch-manipulation"
                                        />
                                        <span className="ml-4 text-base text-gray-700 capitalize select-none">{source.replace(/_/g, ' ')}</span>
                                    </label>
                                ))}
                            </div>
                        </div>

                        {/* Custom Date Range */}
                        <div>
                            <label className="block text-base font-medium text-gray-700 mb-3">
                                Custom Date Range
                            </label>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm text-gray-600 mb-1">From Date</label>
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
                                        className="w-full py-3 px-3 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-base touch-manipulation"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm text-gray-600 mb-1">To Date</label>
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
                                        className="w-full py-3 px-3 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-base touch-manipulation"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="p-4 border-t border-gray-200">
                        <button
                            onClick={() => setShowAdvanced(false)}
                            className="w-full py-3 px-4 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 active:bg-blue-800 touch-manipulation"
                        >
                            Apply Filters
                        </button>
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
                                className="inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
                            >
                                {pill.label}
                                <button
                                    type="button"
                                    onClick={pill.onRemove}
                                    className="ml-2 inline-flex items-center justify-center h-5 w-5 rounded-full text-blue-400 hover:bg-blue-200 hover:text-blue-500 focus:outline-none focus:bg-blue-500 focus:text-white touch-manipulation"
                                >
                                    <XMarkIcon className="h-3 w-3" />
                                </button>
                            </span>
                        ))}
                        <button
                            onClick={clearAllFilters}
                            className="text-sm text-gray-500 hover:text-gray-700 underline ml-2 py-1 px-2 touch-manipulation"
                        >
                            Clear all
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};
