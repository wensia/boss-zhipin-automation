/**
 * 运行日志页面 - 实时显示打招呼任务日志
 */
import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Progress } from '@/components/ui/progress';

interface GreetingLog {
  timestamp: string;
  level: string;
  message: string;
}

interface GreetingStatus {
  status: string;
  target_count: number;
  current_index: number;
  success_count: number;
  failed_count: number;
  progress: number;
  start_time: string | null;
  end_time: string | null;
  elapsed_time: number | null;
  error_message: string | null;
}

export default function Logs() {
  const [logs, setLogs] = useState<GreetingLog[]>([]);
  const [status, setStatus] = useState<GreetingStatus | null>(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const logsEndRef = useRef<HTMLDivElement>(null);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // 轮询日志和状态
  useEffect(() => {
    const fetchData = async () => {
      try {
        // 获取状态
        const statusRes = await fetch('/api/greeting/status');
        const statusData = await statusRes.json();
        setStatus(statusData);

        // 获取日志
        const logsRes = await fetch('/api/greeting/logs?last_n=100');
        const logsData = await logsRes.json();
        setLogs(logsData.logs || []);
      } catch (error) {
        console.error('获取日志失败:', error);
      }
    };

    // 立即执行一次
    fetchData();

    // 每秒轮询
    pollingIntervalRef.current = setInterval(fetchData, 1000);

    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  // 自动滚动到底部
  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

  const getLevelColor = (level: string): string => {
    switch (level.toUpperCase()) {
      case 'INFO':
        return 'text-blue-600';
      case 'WARNING':
        return 'text-yellow-600';
      case 'ERROR':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'idle':
        return <Badge variant="outline">空闲</Badge>;
      case 'running':
        return <Badge className="bg-green-500">运行中</Badge>;
      case 'completed':
        return <Badge className="bg-blue-500">已完成</Badge>;
      case 'error':
        return <Badge variant="destructive">错误</Badge>;
      case 'cancelled':
        return <Badge variant="secondary">已取消</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const formatTime = (timestamp: string): string => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('zh-CN', { hour12: false });
  };

  const formatElapsedTime = (seconds: number | null): string => {
    if (!seconds) return '-';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}分${secs}秒`;
  };

  return (
    <div className="h-full">
      <div className="mb-4">
        <h1 className="text-2xl font-bold">运行日志</h1>
        <p className="text-muted-foreground text-sm">实时显示打招呼任务执行日志</p>
      </div>

      {/* 左右布局 */}
      <div className="grid grid-cols-12 gap-4 h-[calc(100vh-180px)]">
        {/* 左侧：日志显示区 */}
        <div className="col-span-8">
          <Card className="h-full flex flex-col">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle>实时日志</CardTitle>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setAutoScroll(!autoScroll)}
                  >
                    {autoScroll ? '🔒 自动滚动' : '🔓 手动滚动'}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setLogs([])}
                  >
                    清空日志
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="flex-1 p-0 overflow-hidden">
              <ScrollArea className="h-full">
                <div className="p-4 font-mono text-xs space-y-1 bg-gray-950 text-gray-100">
                  {logs.length === 0 ? (
                    <div className="text-gray-500 text-center py-8">
                      暂无日志记录
                    </div>
                  ) : (
                    logs.map((log, index) => (
                      <div key={index} className="flex items-start gap-2 hover:bg-gray-900 px-2 py-1 rounded">
                        <span className="text-gray-500 shrink-0">
                          {formatTime(log.timestamp)}
                        </span>
                        <span className={`shrink-0 font-semibold ${
                          log.level === 'INFO' ? 'text-blue-400' :
                          log.level === 'WARNING' ? 'text-yellow-400' :
                          log.level === 'ERROR' ? 'text-red-400' :
                          'text-gray-400'
                        }`}>
                          [{log.level}]
                        </span>
                        <span className="text-gray-200">{log.message}</span>
                      </div>
                    ))
                  )}
                  <div ref={logsEndRef} />
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>

        {/* 右侧：状态信息区 */}
        <div className="col-span-4 space-y-4">
          {/* 任务状态 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">任务状态</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {status ? (
                <>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">当前状态</span>
                    {getStatusBadge(status.status)}
                  </div>

                  {status.status === 'running' && (
                    <>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-muted-foreground">进度</span>
                          <span className="font-semibold">{status.progress.toFixed(1)}%</span>
                        </div>
                        <Progress value={status.progress} className="h-2" />
                      </div>

                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">当前进度</span>
                        <span className="text-sm font-medium">
                          {status.current_index} / {status.target_count}
                        </span>
                      </div>
                    </>
                  )}

                  {status.error_message && (
                    <div className="p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
                      {status.error_message}
                    </div>
                  )}
                </>
              ) : (
                <div className="text-sm text-muted-foreground">加载中...</div>
              )}
            </CardContent>
          </Card>

          {/* 执行统计 */}
          {status && status.target_count > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">执行统计</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">目标数量</span>
                  <span className="text-lg font-bold">{status.target_count}</span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-green-600">成功</span>
                  <span className="text-lg font-bold text-green-600">
                    {status.success_count}
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-red-600">失败</span>
                  <span className="text-lg font-bold text-red-600">
                    {status.failed_count}
                  </span>
                </div>

                <div className="pt-2 border-t">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">耗时</span>
                    <span className="text-sm font-medium">
                      {formatElapsedTime(status.elapsed_time)}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* 时间信息 */}
          {status && status.start_time && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">时间信息</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">开始时间</span>
                  <span className="font-mono text-xs">
                    {new Date(status.start_time).toLocaleTimeString('zh-CN')}
                  </span>
                </div>

                {status.end_time && (
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">结束时间</span>
                    <span className="font-mono text-xs">
                      {new Date(status.end_time).toLocaleTimeString('zh-CN')}
                    </span>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
