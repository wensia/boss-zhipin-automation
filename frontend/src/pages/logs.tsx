/**
 * 日志页面
 */
import { useState, useEffect } from 'react';
import { useLogs } from '@/hooks/useLogs';
import type { LogEntry, LogLevel, LogAction } from '@/types';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function Logs() {
  const { getLogs, loading } = useLogs();
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [limit] = useState(50);
  const [levelFilter, setLevelFilter] = useState<LogLevel | 'all'>('all');
  const [actionFilter, setActionFilter] = useState<LogAction | 'all'>('all');

  const loadLogs = async () => {
    try {
      const params: any = {
        limit,
        offset: page * limit,
      };
      if (levelFilter !== 'all') params.level = levelFilter;
      if (actionFilter !== 'all') params.action = actionFilter;

      const response = await getLogs(params);
      setLogs(response.logs);
      setTotal(response.total);
    } catch (error) {
      console.error('加载日志失败:', error);
    }
  };

  useEffect(() => {
    loadLogs();
  }, [page, levelFilter, actionFilter]);

  const getLevelBadgeVariant = (level: LogLevel): 'default' | 'secondary' | 'destructive' | 'outline' => {
    switch (level) {
      case 'debug':
        return 'outline';
      case 'info':
        return 'default';
      case 'warning':
        return 'secondary';
      case 'error':
      case 'critical':
        return 'destructive';
      default:
        return 'default';
    }
  };

  const getActionLabel = (action: LogAction): string => {
    const labels: Record<LogAction, string> = {
      task_create: '创建任务',
      task_start: '启动任务',
      task_pause: '暂停任务',
      task_resume: '恢复任务',
      task_complete: '完成任务',
      task_fail: '任务失败',
      task_cancel: '取消任务',
      login_init: '初始化登录',
      login_qrcode_get: '获取二维码',
      login_qrcode_refresh: '刷新二维码',
      login_check: '检查登录',
      login_success: '登录成功',
      login_fail: '登录失败',
      candidate_search: '搜索候选人',
      candidate_contact: '联系候选人',
      candidate_contact_success: '联系成功',
      candidate_contact_fail: '联系失败',
      system_init: '系统初始化',
      system_cleanup: '系统清理',
      system_error: '系统错误',
    };
    return labels[action] || action;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    }).format(date);
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">运行日志</h1>
        <p className="text-muted-foreground mt-2">查看系统运行历史记录</p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>日志列表</CardTitle>
              <CardDescription>共 {total} 条记录</CardDescription>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">级别:</span>
                <Select
                  value={levelFilter}
                  onValueChange={(value) => {
                    setLevelFilter(value as LogLevel | 'all');
                    setPage(0);
                  }}
                >
                  <SelectTrigger className="w-[120px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">全部</SelectItem>
                    <SelectItem value="debug">Debug</SelectItem>
                    <SelectItem value="info">Info</SelectItem>
                    <SelectItem value="warning">Warning</SelectItem>
                    <SelectItem value="error">Error</SelectItem>
                    <SelectItem value="critical">Critical</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">操作:</span>
                <Select
                  value={actionFilter}
                  onValueChange={(value) => {
                    setActionFilter(value as LogAction | 'all');
                    setPage(0);
                  }}
                >
                  <SelectTrigger className="w-[140px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">全部</SelectItem>
                    <SelectItem value="task_create">任务相关</SelectItem>
                    <SelectItem value="login_success">登录相关</SelectItem>
                    <SelectItem value="candidate_contact">候选人相关</SelectItem>
                    <SelectItem value="system_error">系统相关</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button onClick={loadLogs} disabled={loading} variant="outline">
                刷新
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[80px]">ID</TableHead>
                  <TableHead className="w-[100px]">级别</TableHead>
                  <TableHead className="w-[140px]">操作类型</TableHead>
                  <TableHead>消息</TableHead>
                  <TableHead className="w-[120px]">任务</TableHead>
                  <TableHead className="w-[120px]">用户</TableHead>
                  <TableHead className="w-[180px]">时间</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading && logs.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center text-muted-foreground">
                      加载中...
                    </TableCell>
                  </TableRow>
                ) : logs.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center text-muted-foreground">
                      暂无日志记录
                    </TableCell>
                  </TableRow>
                ) : (
                  logs.map((log) => (
                    <TableRow key={log.id}>
                      <TableCell className="font-mono text-xs">{log.id}</TableCell>
                      <TableCell>
                        <Badge variant={getLevelBadgeVariant(log.level)}>
                          {log.level.toUpperCase()}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm">{getActionLabel(log.action)}</span>
                      </TableCell>
                      <TableCell className="max-w-md">
                        <div className="truncate" title={log.message}>
                          {log.message}
                        </div>
                      </TableCell>
                      <TableCell>
                        {log.task_name ? (
                          <span className="text-sm text-muted-foreground truncate block">
                            {log.task_name}
                          </span>
                        ) : (
                          <span className="text-sm text-muted-foreground">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {log.user_name ? (
                          <span className="text-sm text-muted-foreground truncate block">
                            {log.user_name}
                          </span>
                        ) : (
                          <span className="text-sm text-muted-foreground">-</span>
                        )}
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {formatDate(log.created_at)}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-4">
              <div className="text-sm text-muted-foreground">
                第 {page + 1} / {totalPages} 页
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(Math.max(0, page - 1))}
                  disabled={page === 0 || loading}
                >
                  上一页
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
                  disabled={page >= totalPages - 1 || loading}
                >
                  下一页
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
