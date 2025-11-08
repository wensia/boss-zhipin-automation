/**
 * 任务管理 Hook
 */
import { useCallback, useState } from 'react';
import { post, get } from '@/lib/api';
import type { AutomationTask, AutomationTaskCreate } from '@/types';

export function useTasks() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * 创建任务
   */
  const createTask = useCallback(
    async (taskData: AutomationTaskCreate): Promise<AutomationTask> => {
      setLoading(true);
      setError(null);

      try {
        const response = await post<AutomationTask>('/automation/tasks', taskData);
        return response;
      } catch (err) {
        const message = err instanceof Error ? err.message : '创建任务失败';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  /**
   * 启动任务
   */
  const startTask = useCallback(async (taskId: number): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      await post<{ message: string; task_id: number }>(
        `/automation/tasks/${taskId}/start`,
        {}
      );
    } catch (err) {
      const message = err instanceof Error ? err.message : '启动任务失败';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * 暂停任务
   */
  const pauseTask = useCallback(async (taskId: number): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      await post<{ message: string; task_id: number }>(
        `/automation/tasks/${taskId}/pause`,
        {}
      );
    } catch (err) {
      const message = err instanceof Error ? err.message : '暂停任务失败';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * 取消任务
   */
  const cancelTask = useCallback(async (taskId: number): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      await post<{ message: string; task_id: number }>(
        `/automation/tasks/${taskId}/cancel`,
        {}
      );
    } catch (err) {
      const message = err instanceof Error ? err.message : '取消任务失败';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * 获取任务列表
   */
  const getTasks = useCallback(
    async (params?: {
      status?: string;
      limit?: number;
      offset?: number;
    }): Promise<AutomationTask[]> => {
      setLoading(true);
      setError(null);

      try {
        const queryParams = new URLSearchParams();
        if (params?.status) queryParams.append('status', params.status);
        if (params?.limit) queryParams.append('limit', params.limit.toString());
        if (params?.offset) queryParams.append('offset', params.offset.toString());

        const endpoint = `/automation/tasks${
          queryParams.toString() ? `?${queryParams.toString()}` : ''
        }`;

        const response = await get<AutomationTask[]>(endpoint);
        return response;
      } catch (err) {
        const message = err instanceof Error ? err.message : '获取任务列表失败';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  /**
   * 获取单个任务
   */
  const getTask = useCallback(async (taskId: number): Promise<AutomationTask> => {
    setLoading(true);
    setError(null);

    try {
      const response = await get<AutomationTask>(`/automation/tasks/${taskId}`);
      return response;
    } catch (err) {
      const message = err instanceof Error ? err.message : '获取任务详情失败';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    createTask,
    startTask,
    pauseTask,
    cancelTask,
    getTasks,
    getTask,
  };
}
