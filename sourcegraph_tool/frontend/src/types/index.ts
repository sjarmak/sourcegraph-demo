export interface Insight {
  id: number;
  tool: string;
  date: string;
  title: string;
  summary: string;
  topics: string[];
  link?: string;
  snippet?: string;
  created_at: string;
  updated_at: string;
}

export interface InsightFilters {
  tool?: string;
  sources?: string[];
  dateRange?: {
    start: string;
    end: string;
  };
  fromHours?: number;
  keyword?: string;
  q?: string;
  tags?: string[];
  limit?: number;
}

export interface TrendData {
  tool: string;
  date: string;
  count: number;
}
