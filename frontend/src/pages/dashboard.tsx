/**
 * Dashboard 仪表盘页面
 */
import { useEffect, useState } from 'react';
import { Users, MessageSquare, CheckCircle, ListTodo } from 'lucide-react';
import { StatCard } from '@/components/stat-card';
import { useConfig } from '@/hooks/useConfig';
import type { SystemStats } from '@/types';

export function Dashboard() {
  const { getStats, loading } = useConfig();
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [refreshInterval, setRefreshInterval] = useState<number | null>(null);

  const loadStats = async () => {
    try {
      const data = await getStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  useEffect(() => {
    loadStats();

    // 每 30 秒刷新一次
    const interval = window.setInterval(loadStats, 30000);
    setRefreshInterval(interval);

    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  }, []);

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center h-96">
        <p className="text-muted-foreground">加载中...</p>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="flex items-center justify-center h-96">
        <p className="text-muted-foreground">暂无数据</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">仪表盘</h1>
        <p className="text-muted-foreground mt-2">
          Boss 直聘自动化系统概览
        </p>
      </div>

      {/* 系统状态 */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="候选人总数"
          value={stats.candidates.total}
          description={`今日新增 ${stats.candidates.today_added} 人`}
          icon={<Users className="h-4 w-4" />}
        />
        <StatCard
          title="问候总数"
          value={stats.greetings.total}
          description={`成功率 ${stats.greetings.success_rate}%`}
          icon={<MessageSquare className="h-4 w-4" />}
        />
        <StatCard
          title="今日已联系"
          value={`${stats.config.today_contacted} / ${stats.config.daily_limit}`}
          description={`剩余 ${stats.config.remaining_today} 个名额`}
          icon={<CheckCircle className="h-4 w-4" />}
        />
        <StatCard
          title="任务统计"
          value={stats.tasks.total}
          description={`运行中 ${stats.tasks.running} | 已完成 ${stats.tasks.completed}`}
          icon={<ListTodo className="h-4 w-4" />}
        />
      </div>

      {/* 详细统计 */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* 问候统计 */}
        <div className="rounded-lg border bg-card p-6">
          <h3 className="text-lg font-semibold mb-4">问候统计</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">总发送数</span>
              <span className="font-medium">{stats.greetings.total}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">成功数</span>
              <span className="font-medium text-green-600">
                {stats.greetings.success}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">失败数</span>
              <span className="font-medium text-red-600">
                {stats.greetings.total - stats.greetings.success}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">今日发送</span>
              <span className="font-medium">{stats.greetings.today}</span>
            </div>
          </div>
        </div>

        {/* 系统配置 */}
        <div className="rounded-lg border bg-card p-6">
          <h3 className="text-lg font-semibold mb-4">系统配置</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">登录状态</span>
              <span
                className={`px-2 py-1 rounded text-xs font-medium ${
                  stats.config.boss_session_saved
                    ? 'bg-green-100 text-green-700'
                    : 'bg-gray-100 text-gray-700'
                }`}
              >
                {stats.config.boss_session_saved ? '已登录' : '未登录'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">自动模式</span>
              <span
                className={`px-2 py-1 rounded text-xs font-medium ${
                  stats.config.auto_mode_enabled
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-gray-100 text-gray-700'
                }`}
              >
                {stats.config.auto_mode_enabled ? '已启用' : '已禁用'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">反检测</span>
              <span
                className={`px-2 py-1 rounded text-xs font-medium ${
                  stats.config.anti_detection_enabled
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-gray-100 text-gray-700'
                }`}
              >
                {stats.config.anti_detection_enabled ? '已启用' : '已禁用'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">模板数量</span>
              <span className="font-medium">
                {stats.templates.active} / {stats.templates.total}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 快速操作提示 */}
      {!stats.config.boss_session_saved && (
        <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4">
          <div className="flex items-center gap-3">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-yellow-600"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div>
              <h4 className="text-sm font-medium text-yellow-800">
                需要登录
              </h4>
              <p className="text-sm text-yellow-700 mt-1">
                请先在系统设置中登录 Boss 直聘账号，才能使用自动化功能。
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
