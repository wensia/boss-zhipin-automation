/**
 * 通知配置管理 Hook
 */
import { useState, useCallback } from 'react';
import { get, put, post } from '@/lib/api';
import type { NotificationConfig, NotificationConfigUpdate } from '@/types/notification';

export function useNotification() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getConfig = useCallback(async (): Promise<NotificationConfig> => {
    setLoading(true);
    setError(null);
    try {
      return await get<NotificationConfig>('/notification/config');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get notification config';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateConfig = useCallback(
    async (data: NotificationConfigUpdate): Promise<NotificationConfig> => {
      setLoading(true);
      setError(null);
      try {
        return await put<NotificationConfig>('/notification/config', data);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to update notification config';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const testDingtalk = useCallback(async (): Promise<{ success: boolean; message: string }> => {
    setLoading(true);
    setError(null);
    try {
      return await post('/notification/test-dingtalk');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to test dingtalk notification';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const testFeishu = useCallback(async (): Promise<{ success: boolean; message: string }> => {
    setLoading(true);
    setError(null);
    try {
      return await post('/notification/test-feishu');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to test feishu notification';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const testFeishuBitable = useCallback(
    async (): Promise<{ success: boolean; message: string; field_count?: number }> => {
      setLoading(true);
      setError(null);
      try {
        return await post('/notification/test-feishu-bitable');
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to test feishu bitable connection';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const syncGreetingFields = useCallback(
    async (): Promise<{
      success: boolean;
      message: string;
      existing_count: number;
      created_count: number;
      failed_count: number;
      details: any;
    }> => {
      setLoading(true);
      setError(null);
      try {
        return await post('/notification/sync-greeting-fields');
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to sync greeting fields';
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
    getConfig,
    updateConfig,
    testDingtalk,
    testFeishu,
    testFeishuBitable,
    syncGreetingFields,
  };
}
