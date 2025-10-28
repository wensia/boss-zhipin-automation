/**
 * 系统配置管理 Hook
 */
import { useState, useCallback } from 'react';
import { get, post, patch } from '@/lib/api';
import type { SystemConfig, SystemConfigUpdate, SystemStats } from '@/types';

export function useConfig() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getConfig = useCallback(async (): Promise<SystemConfig> => {
    setLoading(true);
    setError(null);
    try {
      return await get<SystemConfig>('/config');
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to get config';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateConfig = useCallback(
    async (data: SystemConfigUpdate): Promise<SystemConfig> => {
      setLoading(true);
      setError(null);
      try {
        return await patch<SystemConfig>('/config', data);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to update config';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const resetDailyCounter = useCallback(async (): Promise<{
    message: string;
    today_contacted: number;
  }> => {
    setLoading(true);
    setError(null);
    try {
      return await post('/config/reset-daily-counter');
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to reset counter';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const incrementDailyCounter = useCallback(async (): Promise<{
    message: string;
    today_contacted: number;
    daily_limit: number;
  }> => {
    setLoading(true);
    setError(null);
    try {
      return await post('/config/increment-daily-counter');
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to increment counter';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const checkDailyLimit = useCallback(async (): Promise<{
    reached_limit: boolean;
    today_contacted: number;
    daily_limit: number;
    remaining: number;
  }> => {
    setLoading(true);
    setError(null);
    try {
      return await get('/config/check-daily-limit');
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to check limit';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const toggleAutoMode = useCallback(async (): Promise<{
    message: string;
    auto_mode_enabled: boolean;
  }> => {
    setLoading(true);
    setError(null);
    try {
      return await post('/config/toggle-auto-mode');
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to toggle auto mode';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const toggleAntiDetection = useCallback(async (): Promise<{
    message: string;
    anti_detection_enabled: boolean;
  }> => {
    setLoading(true);
    setError(null);
    try {
      return await post('/config/toggle-anti-detection');
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : 'Failed to toggle anti detection';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const toggleRandomDelay = useCallback(async (): Promise<{
    message: string;
    random_delay_enabled: boolean;
  }> => {
    setLoading(true);
    setError(null);
    try {
      return await post('/config/toggle-random-delay');
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to toggle random delay';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const saveLoginInfo = useCallback(
    async (username?: string): Promise<{
      message: string;
      boss_username?: string;
      boss_session_saved: boolean;
    }> => {
      setLoading(true);
      setError(null);
      try {
        const params = username
          ? `?username=${encodeURIComponent(username)}`
          : '';
        return await post(`/config/save-login-info${params}`);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Failed to save login info';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const clearLoginInfo = useCallback(async (): Promise<{
    message: string;
    boss_session_saved: boolean;
  }> => {
    setLoading(true);
    setError(null);
    try {
      return await post('/config/clear-login-info');
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to clear login info';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getStats = useCallback(async (): Promise<SystemStats> => {
    setLoading(true);
    setError(null);
    try {
      return await get<SystemStats>('/config/stats');
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to get stats';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    getConfig,
    updateConfig,
    resetDailyCounter,
    incrementDailyCounter,
    checkDailyLimit,
    toggleAutoMode,
    toggleAntiDetection,
    toggleRandomDelay,
    saveLoginInfo,
    clearLoginInfo,
    getStats,
  };
}
