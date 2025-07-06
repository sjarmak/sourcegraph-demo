import { useState, useEffect } from 'react';
import { ApiService } from '../services/api';
import type { Insight, InsightFilters } from '../types';

export const useInsights = (filters?: InsightFilters) => {
  const [insights, setInsights] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchInsights = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const data = await ApiService.getInsights(filters);
        setInsights(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchInsights();
  }, [filters]);

  return { insights, loading, error };
};
