/**
 * 职位列表管理 Hook
 */
import { useCallback, useState } from 'react';
import { get } from '@/lib/api';
import type { JobsResponse } from '@/types';

export function useJobs() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * 获取已沟通的职位列表
   */
  const getJobs = useCallback(async (): Promise<JobsResponse> => {
    setLoading(true);
    setError(null);

    try {
      const response = await get<JobsResponse>('/automation/jobs');
      return response;
    } catch (err) {
      const message = err instanceof Error ? err.message : '获取职位列表失败';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    getJobs,
  };
}
