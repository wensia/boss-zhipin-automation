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
    triggerLogin,
    getQrcode,
    checkLogin,
    refreshQrcode,
    cleanup,
  };
}
