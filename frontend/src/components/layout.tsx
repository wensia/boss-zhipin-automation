/**
 * 应用布局组件 - 左右分栏布局
 */
import { Link, useLocation } from 'react-router-dom';
import { useState, useEffect, useRef } from 'react';
import { LayoutDashboard, Zap, Settings, UserCog, Bell, ChevronDown, Check } from 'lucide-react';
import { toast } from 'sonner';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Progress } from '@/components/ui/progress';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu';
import { useCurrentAccount } from '@/hooks/useCurrentAccount';

const navigation = [
  { name: '快速启动', href: '/wizard', icon: Zap },
  { name: '仪表盘', href: '/', icon: LayoutDashboard },
  { name: '账号管理', href: '/accounts', icon: UserCog },
  { name: '通知设置', href: '/notification', icon: Bell },
  { name: '系统设置', href: '/settings', icon: Settings },
];

interface LayoutProps {
  children: React.ReactNode;
}

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

export function Layout({ children }: LayoutProps) {
  const location = useLocation();
  const [logs, setLogs] = useState<GreetingLog[]>([]);
  const [status, setStatus] = useState<GreetingStatus | null>(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const logsEndRef = useRef<HTMLDivElement>(null);
  const pollingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // 账号管理
  const { currentAccount, allAccounts, switching, switchToAccount } = useCurrentAccount();

  // 轮询日志和状态
  useEffect(() => {
    const fetchData = async () => {
      try {
        const statusRes = await fetch('/api/greeting/status');
        if (!statusRes.ok) {
          // API不可用或没有任务运行，不报错
          return;
        }
        const statusData = await statusRes.json();
        setStatus(statusData);

        const logsRes = await fetch('/api/greeting/logs?last_n=100');
        if (logsRes.ok) {
          const logsData = await logsRes.json();
          setLogs(logsData.logs || []);
        }
      } catch (error) {
        // 静默处理错误，避免控制台大量错误信息
        // console.error('获取日志失败:', error);
      }
    };

    fetchData();
    pollingIntervalRef.current = setInterval(fetchData, 2000); // 改为2秒轮询

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

  // 切换账号处理函数
  const handleSwitchAccount = async (accountId: number) => {
    try {
      toast.loading('正在切换账号...', { id: 'switch-account' });
      await switchToAccount(accountId);
      toast.success('账号切换成功', { id: 'switch-account' });
    } catch (error) {
      toast.error(error instanceof Error ? error.message : '切换失败', { id: 'switch-account' });
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* 左侧：运行日志区域 */}
      <div className="w-[400px] bg-white border-r border-gray-200 flex flex-col">
        {/* 日志标题 */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200">
          <h2 className="text-lg font-bold text-gray-900">运行日志</h2>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setAutoScroll(!autoScroll)}
          >
            {autoScroll ? '🔒' : '🔓'}
          </Button>
        </div>

        {/* 状态信息 */}
        {status && status.status !== 'idle' && (
          <div className="px-4 py-3 border-b border-gray-200 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">状态</span>
              {getStatusBadge(status.status)}
            </div>

            {status.status === 'running' && (
              <>
                <div className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground">进度</span>
                    <span className="font-semibold">{status.progress.toFixed(0)}%</span>
                  </div>
                  <Progress value={status.progress} className="h-1.5" />
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">当前</span>
                  <span>{status.current_index} / {status.target_count}</span>
                </div>
              </>
            )}

            {status.target_count > 0 && (
              <div className="flex items-center justify-between text-xs">
                <span className="text-green-600">成功 {status.success_count}</span>
                <span className="text-red-600">失败 {status.failed_count}</span>
                <span className="text-muted-foreground">耗时 {formatElapsedTime(status.elapsed_time)}</span>
              </div>
            )}
          </div>
        )}

        {/* 日志内容 */}
        <div className="flex-1 overflow-hidden">
          <ScrollArea className="h-full">
            <div className="p-3 font-mono text-xs space-y-0.5 bg-gray-950 text-gray-100 min-h-full">
              {logs.length === 0 ? (
                <div className="text-gray-500 text-center py-8">
                  暂无日志记录
                </div>
              ) : (
                logs.map((log, index) => (
                  <div key={index} className="flex items-start gap-2 hover:bg-gray-900 px-2 py-0.5 rounded">
                    <span className="text-gray-500 shrink-0 text-[10px]">
                      {formatTime(log.timestamp)}
                    </span>
                    <span className={`shrink-0 font-semibold text-[10px] ${
                      log.level === 'INFO' ? 'text-blue-400' :
                      log.level === 'WARNING' ? 'text-yellow-400' :
                      log.level === 'ERROR' ? 'text-red-400' :
                      'text-gray-400'
                    }`}>
                      [{log.level}]
                    </span>
                    <span className="text-gray-200 text-[11px] leading-relaxed">{log.message}</span>
                  </div>
                ))
              )}
              <div ref={logsEndRef} />
            </div>
          </ScrollArea>
        </div>
      </div>

      {/* 右侧：主内容区域 */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* 顶部导航 */}
        <div className="bg-white border-b border-gray-200 shadow-sm">
          {/* Tab导航 */}
          <nav className="flex items-center justify-between px-4 overflow-x-auto">
            <div className="flex space-x-1">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href;
                const Icon = item.icon;

                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`flex items-center px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                      isActive
                        ? 'border-blue-600 text-blue-700'
                        : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                    }`}
                  >
                    <Icon className={`mr-2 h-4 w-4 ${isActive ? 'text-blue-700' : 'text-gray-400'}`} />
                    {item.name}
                  </Link>
                );
              })}
            </div>

            {/* 账号切换 */}
            {currentAccount ? (
              <DropdownMenu>
                <DropdownMenuTrigger>
                  <div className="flex items-center gap-2 px-3 py-2 hover:bg-gray-50 rounded-md cursor-pointer transition-colors">
                    <Avatar>
                      <AvatarImage src={currentAccount.avatar} alt={currentAccount.show_name} />
                      <AvatarFallback>{currentAccount.show_name[0]}</AvatarFallback>
                    </Avatar>
                    <div className="text-left">
                      <div className="text-sm font-medium text-gray-900">
                        {currentAccount.show_name}
                      </div>
                      <div className="text-xs text-gray-500">
                        {currentAccount.company_short_name}
                      </div>
                    </div>
                    <ChevronDown className="h-4 w-4 text-gray-400" />
                  </div>
                </DropdownMenuTrigger>

                <DropdownMenuContent align="end">
                  {allAccounts.map((account) => (
                    <DropdownMenuItem
                      key={account.id}
                      onClick={() => handleSwitchAccount(account.id)}
                      disabled={switching || account.id === currentAccount.id}
                    >
                      <Avatar>
                        <AvatarImage src={account.avatar} alt={account.show_name} />
                        <AvatarFallback>{account.show_name[0]}</AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <div className="text-sm font-medium">{account.show_name}</div>
                        <div className="text-xs text-gray-500">{account.company_short_name}</div>
                      </div>
                      {account.id === currentAccount.id && (
                        <Check className="h-4 w-4 text-blue-600" />
                      )}
                    </DropdownMenuItem>
                  ))}
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => window.location.href = '/accounts'}>
                    <UserCog className="h-4 w-4 mr-2" />
                    管理账号
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <Link to="/accounts">
                <Button variant="outline" size="sm">
                  <UserCog className="h-4 w-4 mr-2" />
                  添加账号
                </Button>
              </Link>
            )}
          </nav>
        </div>

        {/* 主内容 */}
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
