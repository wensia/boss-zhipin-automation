/**
 * 当前账号管理Hook - 全局状态管理
 */
import { useState, useEffect, useCallback } from 'react';
import type { UserAccount } from '@/types/account';

const API_BASE_URL = '/api/accounts';

export function useCurrentAccount() {
  const [currentAccount, setCurrentAccount] = useState<UserAccount | null>(null);
  const [allAccounts, setAllAccounts] = useState<UserAccount[]>([]);
  const [loading, setLoading] = useState(false);
  const [switching, setSwitching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * 获取当前账号
   */
  const fetchCurrentAccount = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/current`);
      if (response.ok) {
        const data = await response.json();
        setCurrentAccount(data);
      } else {
        setCurrentAccount(null);
      }
    } catch (err) {
      console.error('获取当前账号失败:', err);
      setCurrentAccount(null);
    }
  }, []);

  /**
   * 获取所有账号列表
   */
  const fetchAllAccounts = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}`);
      if (response.ok) {
        const data = await response.json();
        setAllAccounts(data);
      }
    } catch (err) {
      console.error('获取账号列表失败:', err);
    }
  }, []);

  /**
   * 切换账号
   */
  const switchToAccount = useCallback(async (accountId: number) => {
    setSwitching(true);
    setError(null);
    try {
      // 调用切换账号API
      const response = await fetch(
        `/api/automation/switch-account/${accountId}`,
        { method: 'POST' }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '切换账号失败');
      }

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.message || '切换账号失败');
      }

      // 重新获取当前账号
      await fetchCurrentAccount();

      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : '切换账号失败';
      setError(message);
      throw err;
    } finally {
      setSwitching(false);
    }
  }, [fetchCurrentAccount]);

  /**
   * 设置激活账号（仅更新配置，不切换浏览器）
   */
  const setActiveAccount = useCallback(async (accountId: number) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/${accountId}/set-active`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('设置当前账号失败');
      }

      await fetchCurrentAccount();
    } catch (err) {
      const message = err instanceof Error ? err.message : '设置当前账号失败';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [fetchCurrentAccount]);

  /**
   * 初始化 - 获取当前账号和账号列表
   */
  useEffect(() => {
    fetchCurrentAccount();
    fetchAllAccounts();
  }, [fetchCurrentAccount, fetchAllAccounts]);

  return {
    currentAccount,
    allAccounts,
    loading,
    switching,
    error,
    switchToAccount,
    setActiveAccount,
    refreshCurrentAccount: fetchCurrentAccount,
    refreshAllAccounts: fetchAllAccounts,
  };
}
