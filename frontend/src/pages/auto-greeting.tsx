import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Play, Square, RotateCcw, Info, CheckCircle, XCircle, AlertCircle, AlertTriangle } from 'lucide-react';

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

interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
}

export default function AutoGreetingPage() {
  const [targetCount, setTargetCount] = useState<number | ''>(10);
  const [status, setStatus] = useState<GreetingStatus>({
    status: 'idle',
    target_count: 0,
    current_index: 0,
    success_count: 0,
    failed_count: 0,
    progress: 0,
    start_time: null,
    end_time: null,
    elapsed_time: null,
    error_message: null
  });
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const logsEndRef = useRef<HTMLDivElement>(null);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // 自动滚动到日志底部
  const scrollToBottom = () => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [logs]);

  // 轮询获取状态和日志
  useEffect(() => {
    const startPolling = () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }

      pollingIntervalRef.current = setInterval(async () => {
        try {
          // 获取状态
          const statusRes = await fetch('/api/greeting/status');
          const statusData = await statusRes.json();
          setStatus(statusData);

          // 获取日志
          const logsRes = await fetch('/api/greeting/logs?last_n=100');
          const logsData = await logsRes.json();
          setLogs(logsData.logs);

          // 如果任务完成或出错，停止轮询
          if (statusData.status !== 'running') {
            if (pollingIntervalRef.current) {
              clearInterval(pollingIntervalRef.current);
              pollingIntervalRef.current = null;
            }
          }
        } catch (error) {
          console.error('Failed to fetch status:', error);
        }
      }, 1000); // 每秒轮询一次
    };

    // 初始加载状态
    const fetchInitialStatus = async () => {
      try {
        const statusRes = await fetch('/api/greeting/status');
        const statusData = await statusRes.json();
        setStatus(statusData);

        const logsRes = await fetch('/api/greeting/logs?last_n=100');
        const logsData = await logsRes.json();
        setLogs(logsData.logs);

        // 如果任务正在运行，开始轮询
        if (statusData.status === 'running') {
          startPolling();
        }
      } catch (error) {
        console.error('Failed to fetch initial status:', error);
      }
    };

    fetchInitialStatus();

    // 清理函数
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  const handleStart = async () => {
    // 验证输入
    const count = targetCount === '' ? 10 : targetCount;
    if (count < 1 || count > 500) {
      alert('请输入1-500之间的数量');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch('/api/greeting/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ target_count: count })
      });

      const data = await response.json();

      if (response.ok) {
        // 开始轮询
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
        }

        pollingIntervalRef.current = setInterval(async () => {
          try {
            const statusRes = await fetch('/api/greeting/status');
            const statusData = await statusRes.json();
            setStatus(statusData);

            const logsRes = await fetch('/api/greeting/logs?last_n=100');
            const logsData = await logsRes.json();
            setLogs(logsData.logs);

            if (statusData.status !== 'running') {
              if (pollingIntervalRef.current) {
                clearInterval(pollingIntervalRef.current);
                pollingIntervalRef.current = null;
              }
            }
          } catch (error) {
            console.error('Polling error:', error);
          }
        }, 1000);
      } else {
        alert(data.detail || '启动失败');
      }
    } catch (error) {
      console.error('Failed to start greeting:', error);
      alert('启动失败，请检查后端服务');
    } finally {
      setIsLoading(false);
    }
  };

  const handleStop = async () => {
    try {
      const response = await fetch('/api/greeting/stop', {
        method: 'POST'
      });

      if (response.ok) {
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
        }
      } else {
        const data = await response.json();
        alert(data.detail || '停止失败');
      }
    } catch (error) {
      console.error('Failed to stop greeting:', error);
      alert('停止失败');
    }
  };

  const handleReset = async () => {
    try {
      const response = await fetch('/api/greeting/reset', {
        method: 'POST'
      });

      if (response.ok) {
        setLogs([]);
        const statusRes = await fetch('/api/greeting/status');
        const statusData = await statusRes.json();
        setStatus(statusData);
      } else {
        const data = await response.json();
        alert(data.detail || '重置失败');
      }
    } catch (error) {
      console.error('Failed to reset:', error);
      alert('重置失败');
    }
  };

  const handleForceReset = async () => {
    const confirmed = window.confirm(
      '⚠️ 强制重置将立即停止所有正在运行的任务并清空状态。\n\n' +
      '这个操作用于修复任务卡在"运行中"状态但实际已停止的问题。\n\n' +
      '确定要继续吗？'
    );

    if (!confirmed) {
      return;
    }

    try {
      const response = await fetch('/api/greeting/force-reset', {
        method: 'POST'
      });

      if (response.ok) {
        setLogs([]);
        // 停止轮询
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
        }
        // 刷新状态
        const statusRes = await fetch('/api/greeting/status');
        const statusData = await statusRes.json();
        setStatus(statusData);
        alert('✅ 强制重置成功');
      } else {
        const data = await response.json();
        alert(data.detail || '强制重置失败');
      }
    } catch (error) {
      console.error('Failed to force reset:', error);
      alert('强制重置失败');
    }
  };

  const getStatusBadge = () => {
    switch (status.status) {
      case 'running':
        return <Badge className="bg-blue-500">运行中</Badge>;
      case 'completed':
        return <Badge className="bg-green-500">已完成</Badge>;
      case 'error':
        return <Badge className="bg-red-500">出错</Badge>;
      case 'cancelled':
        return <Badge className="bg-yellow-500">已停止</Badge>;
      default:
        return <Badge variant="outline">空闲</Badge>;
    }
  };

  const getLogIcon = (level: string) => {
    switch (level) {
      case 'INFO':
        return <Info className="h-4 w-4 text-blue-500" />;
      case 'WARNING':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      case 'ERROR':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <CheckCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const formatTime = (seconds: number | null) => {
    if (seconds === null) return '--';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}分${secs}秒`;
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">自动打招呼</h1>
          <p className="text-muted-foreground mt-1">批量向推荐候选人发送招呼消息</p>
        </div>
        {getStatusBadge()}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左侧：控制面板 */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>控制面板</CardTitle>
              <CardDescription>设置并启动打招呼任务</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="target-count">打招呼数量</Label>
                <Input
                  id="target-count"
                  type="number"
                  min="1"
                  max="500"
                  value={targetCount}
                  onChange={(e) => {
                    const value = e.target.value;
                    if (value === '') {
                      setTargetCount('');
                    } else {
                      const num = parseInt(value);
                      if (!isNaN(num)) {
                        setTargetCount(num);
                      }
                    }
                  }}
                  onBlur={(e) => {
                    // 失去焦点时，如果为空则设置为默认值10
                    if (e.target.value === '') {
                      setTargetCount(10);
                    }
                  }}
                  disabled={status.status === 'running'}
                  className="mt-2"
                />
                <p className="text-sm text-muted-foreground mt-1">
                  最多可设置 500 人，建议分批次进行，避免触发平台限制
                </p>
              </div>

              <div className="flex gap-2">
                <Button
                  onClick={handleStart}
                  disabled={status.status === 'running' || isLoading}
                  className="flex-1"
                >
                  <Play className="h-4 w-4 mr-2" />
                  开始
                </Button>
                <Button
                  onClick={handleStop}
                  disabled={status.status !== 'running'}
                  variant="destructive"
                  className="flex-1"
                >
                  <Square className="h-4 w-4 mr-2" />
                  停止
                </Button>
              </div>

              <Button
                onClick={handleReset}
                disabled={status.status === 'running'}
                variant="outline"
                className="w-full"
              >
                <RotateCcw className="h-4 w-4 mr-2" />
                重置
              </Button>

              {status.status === 'running' && (
                <Button
                  onClick={handleForceReset}
                  variant="destructive"
                  className="w-full"
                >
                  <AlertTriangle className="h-4 w-4 mr-2" />
                  强制重置（用于修复卡死状态）
                </Button>
              )}

              {status.error_message && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{status.error_message}</AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* 统计信息 */}
          <Card className="mt-4">
            <CardHeader>
              <CardTitle>统计信息</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">目标数量</span>
                <span className="font-medium">{status.target_count}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">当前进度</span>
                <span className="font-medium">{status.current_index} / {status.target_count}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">成功数</span>
                <span className="font-medium text-green-600">{status.success_count}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">失败数</span>
                <span className="font-medium text-red-600">{status.failed_count}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">耗时</span>
                <span className="font-medium">{formatTime(status.elapsed_time)}</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 右侧：进度和日志 */}
        <div className="lg:col-span-2 space-y-4">
          {/* 进度条 */}
          <Card>
            <CardHeader>
              <CardTitle>执行进度</CardTitle>
              <CardDescription>
                {status.progress.toFixed(1)}% 完成
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Progress value={status.progress} className="w-full" />
              <p className="text-sm text-muted-foreground mt-2">
                {status.status === 'running' && `正在处理第 ${status.current_index} 个候选人...`}
                {status.status === 'completed' && `✅ 任务完成！成功 ${status.success_count} 个，失败 ${status.failed_count} 个`}
                {status.status === 'idle' && '等待开始...'}
              </p>
            </CardContent>
          </Card>

          {/* 日志面板 */}
          <Card className="flex flex-col" style={{ height: '600px' }}>
            <CardHeader>
              <CardTitle>运行日志</CardTitle>
              <CardDescription>实时显示任务执行日志</CardDescription>
            </CardHeader>
            <CardContent className="flex-1 overflow-hidden">
              <div className="h-full overflow-y-auto bg-gray-50 rounded-lg p-4 font-mono text-sm space-y-1">
                {logs.length === 0 ? (
                  <p className="text-muted-foreground text-center py-8">
                    暂无日志，点击"开始"启动任务
                  </p>
                ) : (
                  logs.map((log, index) => (
                    <div
                      key={index}
                      className="flex items-start gap-2 py-1 border-b border-gray-200 last:border-0"
                    >
                      {getLogIcon(log.level)}
                      <span className="text-xs text-gray-500 w-32 flex-shrink-0">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </span>
                      <span className="flex-1">{log.message}</span>
                    </div>
                  ))
                )}
                <div ref={logsEndRef} />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
