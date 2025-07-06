export interface Insight {
  id: number;
  tool: string;
  date: string;
  title: string;
  summary: string;
  topics: string[];
  link?: string;
  created_at: string;
  updated_at: string;
}

export interface InsightFilters {
  tool?: string;
  dateRange?: {
    start: string;
    end: string;
  };
  keyword?: string;
  tags?: string[];
}

export interface TrendData {
  tool: string;
  date: string;
  count: number;
}
