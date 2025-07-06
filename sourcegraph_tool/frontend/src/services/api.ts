import type { Insight, InsightFilters, TrendData } from '../types';

const API_BASE_URL = 'http://localhost:8000';

export class ApiService {
  private static async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }

  static async getInsights(filters?: InsightFilters): Promise<Insight[]> {
    const params = new URLSearchParams();
    
    if (filters?.tool) params.append('tool', filters.tool);
    if (filters?.sources?.length) params.append('sources', filters.sources.join(','));
    if (filters?.keyword) params.append('keyword', filters.keyword);
    if (filters?.q) params.append('q', filters.q);
    if (filters?.dateRange?.start) params.append('date_from', filters.dateRange.start);
    if (filters?.dateRange?.end) params.append('date_to', filters.dateRange.end);
    if (filters?.fromHours) params.append('from_hours', filters.fromHours.toString());
    if (filters?.tags?.length) params.append('tags', filters.tags.join(','));
    // Only send limit if explicitly set (not undefined)
    if (filters?.limit !== undefined) params.append('limit', filters.limit.toString());

    const queryString = params.toString();
    const endpoint = queryString ? `/api/insights?${queryString}` : '/api/insights';
    
    return this.request<Insight[]>(endpoint);
  }

  static async getTrends(period: string = '7d'): Promise<TrendData[]> {
    return this.request<TrendData[]>(`/api/insights/trends?period=${period}`);
  }

  static async getTools(): Promise<string[]> {
    return this.request<string[]>('/api/insights/tools');
  }

  static async getSources(): Promise<string[]> {
    return this.request<string[]>('/api/insights/sources');
  }

  static async scrapeFeeds(hoursBack: number = 24): Promise<{ message: string; status: string }> {
    return this.request<{ message: string; status: string }>(`/api/scrape-feeds?hours_back=${hoursBack}`, {
      method: 'POST'
    });
  }

  static async getScrapeStatus(): Promise<{
    total_insights_24h: number;
    insights_by_tool: Record<string, number>;
    last_updated: string;
  }> {
    return this.request<{
      total_insights_24h: number;
      insights_by_tool: Record<string, number>;
      last_updated: string;
    }>('/api/scrape-feeds/status');
  }
}
