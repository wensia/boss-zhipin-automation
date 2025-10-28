/**
 * 日志管理 Hook
 */
import { useState, useCallback } from 'react';
import { get } from '@/lib/api';
import type { LogsResponse, LogLevel, LogAction } from '@/types';

export function useLogs() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getLogs = useCallback(
    async (params?: {
      limit?: number;
      offset?: number;
      level?: LogLevel;
      action?: LogAction;
      task_id?: number;
    }): Promise<LogsResponse> => {
      setLoading(true);
      setError(null);
      try {
        const queryParams = new URLSearchParams();
        if (params?.limit) queryParams.set('limit', params.limit.toString());
        if (params?.offset) queryParams.set('offset', params.offset.toString());
        if (params?.level) queryParams.set('level', params.level);
        if (params?.action) queryParams.set('action', params.action);
        if (params?.task_id) queryParams.set('task_id', params.task_id.toString());

        const endpoint = `/logs${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
        return await get<LogsResponse>(endpoint);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to get logs';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return {
    loading,
    error,
    getLogs,
  };
}
