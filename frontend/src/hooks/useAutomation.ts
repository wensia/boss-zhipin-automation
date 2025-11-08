/**
 * 自动化任务管理 Hook
 */
import { useState, useCallback } from 'react';
import { get, post, del } from '@/lib/api';
import type {
  AutomationTask,
  AutomationTaskCreate,
  AutomationStatus,
  TaskStatus,
  UserInfo,
} from '@/types';
import type { FilterOptions } from '@/types/filters';

export function useAutomation() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getTasks = useCallback(
    async (status?: TaskStatus): Promise<AutomationTask[]> => {
      setLoading(true);
      setError(null);
      try {
        const endpoint = status
          ? `/automation/tasks?status=${status}`
          : '/automation/tasks';
        return await get<AutomationTask[]>(endpoint);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to get tasks';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const getTask = useCallback(async (id: number): Promise<AutomationTask> => {
    setLoading(true);
    setError(null);
    try {
      return await get<AutomationTask>(`/automation/tasks/${id}`);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get task';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const createTask = useCallback(
    async (data: AutomationTaskCreate): Promise<AutomationTask> => {
      setLoading(true);
      setError(null);
      try {
        return await post<AutomationTask>('/automation/tasks', data);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to create task';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const startTask = useCallback(
    async (id: number): Promise<{ message: string; task_id: number }> => {
      setLoading(true);
      setError(null);
      try {
        return await post(`/automation/tasks/${id}/start`);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to start task';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const pauseTask = useCallback(
    async (id: number): Promise<{ message: string; task_id: number }> => {
      setLoading(true);
      setError(null);
      try {
        return await post(`/automation/tasks/${id}/pause`);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to pause task';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const cancelTask = useCallback(
    async (id: number): Promise<{ message: string; task_id: number }> => {
      setLoading(true);
      setError(null);
      try {
        return await post(`/automation/tasks/${id}/cancel`);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to cancel task';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const deleteTask = useCallback(
    async (id: number): Promise<{ message: string; task_id: number }> => {
      setLoading(true);
      setError(null);
      try {
        return await del(`/automation/tasks/${id}`);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to delete task';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const getStatus = useCallback(async (): Promise<AutomationStatus> => {
    setLoading(true);
    setError(null);
    try {
      return await get<AutomationStatus>('/automation/status');
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to get status';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const triggerLogin = useCallback(async (): Promise<{
    message: string;
    logged_in: boolean;
  }> => {
    setLoading(true);
    setError(null);
    try {
      return await post('/automation/login');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to login';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const initBrowser = useCallback(async (
    headless: boolean = true,
    com_id?: number
  ): Promise<{
    success: boolean;
    message: string;
    headless: boolean;
    service_initialized: boolean;
    com_id?: number;
  }> => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({ headless: headless.toString() });
      if (com_id) {
        params.append('com_id', com_id.toString());
      }
      return await post(`/automation/init?${params.toString()}`);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to init browser';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getQrcode = useCallback(async (): Promise<{
    success: boolean;
    qrcode: string;
    message: string;
  }> => {
    setLoading(true);
    setError(null);
    try {
      return await get('/automation/qrcode');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get qrcode';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const checkLogin = useCallback(async (): Promise<{
    logged_in: boolean;
    user_info: UserInfo | null;
    message: string;
  }> => {
    setLoading(true);
    setError(null);
    try {
      return await get('/automation/check-login');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to check login';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshQrcode = useCallback(async (): Promise<{
    need_refresh: boolean;
    qrcode: string;
    message: string;
  }> => {
    setLoading(true);
    setError(null);
    try {
      return await get('/automation/refresh-qrcode');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to refresh qrcode';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const cleanup = useCallback(async (): Promise<{ message: string }> => {
    setLoading(true);
    setError(null);
    try {
      return await post('/automation/cleanup');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to cleanup';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getRecommendedCandidates = useCallback(async (maxResults: number = 50): Promise<{
    success: boolean;
    count: number;
    candidates: any[];
  }> => {
    setLoading(true);
    setError(null);
    try {
      return await get(`/automation/recommend-candidates?max_results=${maxResults}`);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get recommended candidates';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getAvailableJobs = useCallback(async (): Promise<{
    success: boolean;
    jobs: Array<{ value: string; label: string }>;
    total: number;
    message: string;
  }> => {
    setLoading(true);
    setError(null);
    try {
      return await get('/automation/available-jobs');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get available jobs';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const selectJob = useCallback(async (jobValue: string): Promise<{
    success: boolean;
    message: string;
    selected_job?: string;
    available_jobs?: Array<{ value: string; label: string }>;
  }> => {
    setLoading(true);
    setError(null);
    try {
      return await post(`/automation/select-job?job_value=${encodeURIComponent(jobValue)}`);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to select job';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const applyFilters = useCallback(async (filters: FilterOptions): Promise<{
    success: boolean;
    message: string;
    applied_count: number;
    failed_count: number;
    details?: any;
  }> => {
    setLoading(true);
    setError(null);
    try {
      return await post('/automation/apply-filters', filters);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to apply filters';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    getTasks,
    getTask,
    createTask,
    startTask,
    pauseTask,
    cancelTask,
    deleteTask,
    getStatus,
    initBrowser,
    triggerLogin,
    getQrcode,
    getQRCode: getQrcode, // 别名，保持向后兼容
    checkLogin,
    refreshQrcode,
    cleanup,
    getRecommendedCandidates,
    getAvailableJobs,
    selectJob,
    applyFilters,
  };
}
