/**
 * 账号管理Hook
 */
import { useState } from 'react';
import type { UserAccount, UserAccountCreate, UserAccountUpdate } from '@/types/account';

const API_BASE_URL = 'http://localhost:27421/api/accounts';

export function useAccounts() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * 获取所有账号列表
   */
  const getAccounts = async (skip: number = 0, limit: number = 100): Promise<UserAccount[]> => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}?skip=${skip}&limit=${limit}`);
      if (!response.ok) {
        throw new Error(`获取账号列表失败: ${response.statusText}`);
      }
      const data = await response.json();
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : '获取账号列表失败';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * 根据ID获取账号详情
   */
  const getAccount = async (accountId: number): Promise<UserAccount> => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/${accountId}`);
      if (!response.ok) {
        throw new Error(`获取账号详情失败: ${response.statusText}`);
      }
      const data = await response.json();
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : '获取账号详情失败';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * 根据comId获取账号
   */
  const getAccountByComId = async (comId: number): Promise<UserAccount> => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/by-comid/${comId}`);
      if (!response.ok) {
        throw new Error(`获取账号详情失败: ${response.statusText}`);
      }
      const data = await response.json();
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : '获取账号详情失败';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * 创建新账号
   */
  const createAccount = async (accountData: UserAccountCreate): Promise<UserAccount> => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(API_BASE_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(accountData),
      });
      if (!response.ok) {
        throw new Error(`创建账号失败: ${response.statusText}`);
      }
      const data = await response.json();
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : '创建账号失败';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * 更新账号信息
   */
  const updateAccount = async (
    accountId: number,
    accountData: UserAccountUpdate
  ): Promise<UserAccount> => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/${accountId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(accountData),
      });
      if (!response.ok) {
        throw new Error(`更新账号失败: ${response.statusText}`);
      }
      const data = await response.json();
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : '更新账号失败';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * 删除账号
   */
  const deleteAccount = async (accountId: number): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/${accountId}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error(`删除账号失败: ${response.statusText}`);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : '删除账号失败';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * 获取当前激活的账号
   */
  const getCurrentAccount = async (): Promise<UserAccount | null> => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/current`);
      if (!response.ok) {
        if (response.status === 404) {
          return null;
        }
        throw new Error(`获取当前账号失败: ${response.statusText}`);
      }
      const data = await response.json();
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : '获取当前账号失败';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * 设置当前激活账号
   */
  const setActiveAccount = async (accountId: number): Promise<UserAccount> => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/${accountId}/set-active`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error(`设置当前账号失败: ${response.statusText}`);
      }
      const data = await response.json();
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : '设置当前账号失败';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * 切换账号（同时切换浏览器context）
   */
  const switchAccount = async (accountId: number): Promise<any> => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:27421/api/automation/switch-account/${accountId}`, {
        method: 'POST',
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `切换账号失败: ${response.statusText}`);
      }
      const data = await response.json();
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : '切换账号失败';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * 验证账号登录状态
   */
  const verifyAccountLogin = async (accountId: number): Promise<any> => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/${accountId}/verify-login`);
      if (!response.ok) {
        throw new Error(`验证登录状态失败: ${response.statusText}`);
      }
      const data = await response.json();
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : '验证登录状态失败';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    error,
    getAccounts,
    getAccount,
    getAccountByComId,
    createAccount,
    updateAccount,
    deleteAccount,
    getCurrentAccount,
    setActiveAccount,
    switchAccount,
    verifyAccountLogin,
  };
}
