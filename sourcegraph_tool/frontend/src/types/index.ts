export interface Insight {
  id: number;
  tool: string;  // Legacy field for backward compatibility
  source?: string;  // New field: where content came from
  mentioned_tools?: string[];  // New field: coding agents mentioned
  mentioned_concepts?: string[];  // New field: AI/coding concepts mentioned
  date: string;
  title: string;
  summary: string;
  topics: string[];
  link?: string;
  snippet?: string;
  matched_keywords?: string[];
  source_type?: string;
  created_at: string;
  updated_at: string;
}

export interface InsightFilters {
  tool?: string;
  sources?: string[];
  mentioned_tools?: string[];
  matched_keywords?: string[];
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
