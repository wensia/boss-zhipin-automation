/**
 * 系统设置页面
 */
import { useEffect, useState, useRef } from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { useConfig } from '@/hooks/useConfig';
import { useAutomation } from '@/hooks/useAutomation';
import type { SystemConfig, UserInfo } from '@/types';

export function Settings() {
  const {
    getConfig,
    updateConfig,
    toggleAutoMode,
    toggleAntiDetection,
    toggleRandomDelay,
    clearLoginInfo,
    testFeishuConnection,
    syncFeishuFields,
    toggleFeishu,
    loading,
  } = useConfig();
  const { getStatus, getQrcode, checkLogin, refreshQrcode } = useAutomation();

  const [config, setConfig] = useState<SystemConfig | null>(null);
  const [automationStatus, setAutomationStatus] = useState<any>(null);
  const [showClearDialog, setShowClearDialog] = useState(false);
  const [showQrcodeDialog, setShowQrcodeDialog] = useState(false);
  const [qrcodeUrl, setQrcodeUrl] = useState<string>('');
  const [checkingLogin, setCheckingLogin] = useState(false);
  const [refreshCount, setRefreshCount] = useState(0);
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const refreshCountRef = useRef(0);
  const [editedConfig, setEditedConfig] = useState({
    daily_limit: 100,
    rest_interval: 15,
    rest_duration: 60,
  });

  // 飞书配置状态
  const [feishuConfig, setFeishuConfig] = useState({
    feishu_app_id: '',
    feishu_app_secret: '',
    feishu_app_token: '',
    feishu_table_id: '',
  });
  const [feishuTestResult, setFeishuTestResult] = useState<{
    success: boolean;
    message: string;
  } | null>(null);
  const [feishuTesting, setFeishuTesting] = useState(false);
  const [feishuSyncing, setFeishuSyncing] = useState(false);

  const loadConfig = async () => {
    try {
      const data = await getConfig();
      setConfig(data);
      setEditedConfig({
        daily_limit: data.daily_limit,
        rest_interval: data.rest_interval,
        rest_duration: data.rest_duration,
      });
      // 加载飞书配置
      setFeishuConfig({
        feishu_app_id: data.feishu_app_id || '',
        feishu_app_secret: data.feishu_app_secret || '',
        feishu_app_token: data.feishu_app_token || '',
        feishu_table_id: data.feishu_table_id || '',
      });
    } catch (error) {
      console.error('Failed to load config:', error);
    }
  };

  const loadAutomationStatus = async () => {
    try {
      const status = await getStatus();
      setAutomationStatus(status);
    } catch (error) {
      console.error('Failed to load automation status:', error);
    }
  };

  useEffect(() => {
    loadConfig();
    loadAutomationStatus();
  }, []);

  const handleSaveConfig = async () => {
    try {
      await updateConfig(editedConfig);
      await loadConfig();
      toast.success('配置已保存');
    } catch (error) {
      console.error('Failed to save config:', error);
      toast.error('保存失败');
    }
  };

  const handleToggleAutoMode = async () => {
    try {
      await toggleAutoMode();
      await loadConfig();
    } catch (error) {
      console.error('Failed to toggle auto mode:', error);
    }
  };

  const handleToggleAntiDetection = async () => {
    try {
      await toggleAntiDetection();
      await loadConfig();
    } catch (error) {
      console.error('Failed to toggle anti detection:', error);
    }
  };

  const handleToggleRandomDelay = async () => {
    try {
      await toggleRandomDelay();
      await loadConfig();
    } catch (error) {
      console.error('Failed to toggle random delay:', error);
    }
  };

  // 飞书配置处理函数
  const handleSaveFeishuConfig = async () => {
    try {
      await updateConfig(feishuConfig);
      await loadConfig();
      toast.success('飞书配置已保存');
      setFeishuTestResult(null);
    } catch (error) {
      console.error('Failed to save feishu config:', error);
      toast.error('保存飞书配置失败');
    }
  };

  const handleTestFeishuConnection = async () => {
    setFeishuTesting(true);
    setFeishuTestResult(null);
    try {
      // 先保存配置
      await updateConfig(feishuConfig);
      // 再测试连接
      const result = await testFeishuConnection();
      setFeishuTestResult(result);
      if (result.success) {
        toast.success(result.message);
      } else {
        toast.error(result.message);
      }
    } catch (error) {
      console.error('Failed to test feishu connection:', error);
      toast.error('测试连接失败');
    } finally {
      setFeishuTesting(false);
    }
  };

  const handleSyncFeishuFields = async () => {
    setFeishuSyncing(true);
    try {
      const result = await syncFeishuFields();
      if (result.success) {
        toast.success(result.message);
      } else {
        toast.error(result.message);
      }
    } catch (error) {
      console.error('Failed to sync feishu fields:', error);
      toast.error('同步字段失败');
    } finally {
      setFeishuSyncing(false);
    }
  };

  const handleToggleFeishu = async () => {
    try {
      const result = await toggleFeishu();
      await loadConfig();
      toast.success(result.message);
    } catch (error) {
      console.error('Failed to toggle feishu:', error);
      toast.error('切换飞书同步状态失败');
    }
  };

  const loginCheckInterval = useRef<number | null>(null);

  const handleLogin = async () => {
    try {
      // 获取二维码或检查已登录状态
      const result = await getQrcode();

      if (result.success) {
        // 检查是否已经登录
        if ((result as any).already_logged_in) {
          // 已登录，直接显示用户信息
          const userInfo = (result as any).user_info;
          if (userInfo) {
            setUserInfo(userInfo);
            toast.success(`欢迎回来，${userInfo.showName || userInfo.name}！`);
          } else {
            toast.success('登录成功！');
          }

          // 刷新配置和状态
          await loadConfig();
          await loadAutomationStatus();
          return;
        }

        // 需要扫码登录
        if (result.qrcode) {
          // 显示二维码对话框
          setQrcodeUrl(result.qrcode);
          setShowQrcodeDialog(true);
          setCheckingLogin(true);
          setRefreshCount(0);
          refreshCountRef.current = 0;

          // 开始轮询检查登录状态
          startLoginCheck();

          toast.info('请使用 Boss 直聘 APP 扫描二维码登录');
        } else {
          toast.error(result.message || '获取二维码失败');
        }
      } else {
        toast.error(result.message || '登录失败');
      }
    } catch (error) {
      console.error('Failed to login:', error);
      toast.error('登录失败');
    }
  };

  const startLoginCheck = () => {
    // 每 2 秒检查一次登录状态和二维码刷新
    loginCheckInterval.current = window.setInterval(async () => {
      try {
        // 检查登录状态
        const loginResult = await checkLogin();

        if (loginResult.logged_in) {
          // 登录成功
          stopLoginCheck();
          setShowQrcodeDialog(false);

          // 保存用户信息
          if (loginResult.user_info) {
            setUserInfo(loginResult.user_info);
            toast.success(`欢迎，${loginResult.user_info.showName || loginResult.user_info.name}！`);
          } else {
            toast.success('登录成功！');
          }

          await loadConfig();
          await loadAutomationStatus();
          return;
        }

        // 如果有错误消息，显示
        if (loginResult.message && loginResult.message !== '等待扫码') {
          toast.error(loginResult.message);
        }

        // 检查二维码是否需要刷新
        const refreshResult = await refreshQrcode();

        if (refreshResult.need_refresh) {
          // 需要刷新二维码
          refreshCountRef.current += 1;
          const currentCount = refreshCountRef.current;
          setRefreshCount(currentCount);

          if (currentCount >= 5) {
            // 达到最大刷新次数
            stopLoginCheck();
            setShowQrcodeDialog(false);
            toast.error('二维码已过期多次，请稍后重试');
            return;
          }

          if (refreshResult.qrcode) {
            // 更新二维码
            setQrcodeUrl(refreshResult.qrcode);
            toast.info(`二维码已自动刷新 (${currentCount}/5)`);
          } else {
            toast.error('二维码刷新失败');
          }
        }
      } catch (error) {
        console.error('Failed to check login or refresh qrcode:', error);
      }
    }, 2000);
  };

  const stopLoginCheck = () => {
    if (loginCheckInterval.current) {
      clearInterval(loginCheckInterval.current);
      loginCheckInterval.current = null;
    }
    setCheckingLogin(false);
  };

  const handleCloseQrcodeDialog = () => {
    stopLoginCheck();
    setShowQrcodeDialog(false);
    setQrcodeUrl('');
  };

  // 清理轮询
  useEffect(() => {
    return () => {
      stopLoginCheck();
    };
  }, []);

  const handleClearLogin = () => {
    setShowClearDialog(true);
  };

  const confirmClearLogin = async () => {
    try {
      await clearLoginInfo();
      await loadConfig();
      await loadAutomationStatus();
      toast.success('登录信息已清除');
    } catch (error) {
      console.error('Failed to clear login:', error);
      toast.error('清除失败');
    } finally {
      setShowClearDialog(false);
    }
  };

  if (!config) {
    return (
      <div className="flex items-center justify-center h-96">
        <p className="text-muted-foreground">加载中...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">系统设置</h1>
        <p className="text-muted-foreground mt-2">配置系统参数和登录状态</p>
      </div>

      {/* 登录设置 */}
      <Card>
        <CardHeader>
          <CardTitle>登录设置</CardTitle>
          <CardDescription>管理 Boss 直聘账号登录状态</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <p className="text-sm font-medium">登录状态</p>
              <p className="text-sm text-muted-foreground">
                {config.boss_session_saved ? '已登录' : '未登录'}
                {config.boss_username && ` (${config.boss_username})`}
              </p>
            </div>
            <div className="flex gap-2">
              {!automationStatus?.is_logged_in ? (
                <Button onClick={handleLogin} disabled={loading}>
                  登录
                </Button>
              ) : (
                <Button variant="outline" onClick={handleClearLogin} disabled={loading}>
                  清除登录
                </Button>
              )}
            </div>
          </div>

          {!config.boss_session_saved && (
            <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4">
              <p className="text-sm text-yellow-800">
                请先登录 Boss 直聘账号才能使用自动化功能。点击"登录"按钮后，系统会打开浏览器窗口，请在窗口中完成登录操作。
              </p>
            </div>
          )}

          {/* 用户信息 */}
          {userInfo && (
            <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
              <div className="flex items-center space-x-4">
                {userInfo.avatar && (
                  <img
                    src={userInfo.avatar}
                    alt={userInfo.showName || userInfo.name}
                    className="w-16 h-16 rounded-full object-cover"
                  />
                )}
                <div className="flex-1 space-y-1">
                  <p className="text-sm font-medium">
                    {userInfo.showName || userInfo.name}
                  </p>
                  {userInfo.brandName && (
                    <p className="text-xs text-muted-foreground">
                      {userInfo.brandName}
                    </p>
                  )}
                  {userInfo.email && (
                    <p className="text-xs text-muted-foreground">
                      {userInfo.email}
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 自动化设置 */}
      <Card>
        <CardHeader>
          <CardTitle>自动化设置</CardTitle>
          <CardDescription>配置自动化行为和反检测功能</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label>自动模式</Label>
              <p className="text-sm text-muted-foreground">
                启用后系统将自动执行任务
              </p>
            </div>
            <Switch
              checked={config.auto_mode_enabled}
              onCheckedChange={handleToggleAutoMode}
              disabled={loading}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label>反检测模式</Label>
              <p className="text-sm text-muted-foreground">
                隐藏自动化特征，避免被识别
              </p>
            </div>
            <Switch
              checked={config.anti_detection_enabled}
              onCheckedChange={handleToggleAntiDetection}
              disabled={loading}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label>随机延迟</Label>
              <p className="text-sm text-muted-foreground">
                在操作之间添加随机延迟
              </p>
            </div>
            <Switch
              checked={config.random_delay_enabled}
              onCheckedChange={handleToggleRandomDelay}
              disabled={loading}
            />
          </div>
        </CardContent>
      </Card>

      {/* 限制设置 */}
      <Card>
        <CardHeader>
          <CardTitle>限制设置</CardTitle>
          <CardDescription>配置每日限制和休息间隔</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-2">
            <Label htmlFor="daily_limit">每日最大联系数</Label>
            <Input
              id="daily_limit"
              type="number"
              min="1"
              max="500"
              value={editedConfig.daily_limit}
              onChange={(e) =>
                setEditedConfig({
                  ...editedConfig,
                  daily_limit: parseInt(e.target.value),
                })
              }
            />
            <p className="text-sm text-muted-foreground">
              当前已联系 {config.today_contacted} 人
            </p>
          </div>

          <div className="grid gap-2">
            <Label htmlFor="rest_interval">休息间隔（分钟）</Label>
            <Input
              id="rest_interval"
              type="number"
              min="5"
              max="60"
              value={editedConfig.rest_interval}
              onChange={(e) =>
                setEditedConfig({
                  ...editedConfig,
                  rest_interval: parseInt(e.target.value),
                })
              }
            />
            <p className="text-sm text-muted-foreground">
              每隔多少分钟休息一次
            </p>
          </div>

          <div className="grid gap-2">
            <Label htmlFor="rest_duration">休息时长（秒）</Label>
            <Input
              id="rest_duration"
              type="number"
              min="30"
              max="300"
              value={editedConfig.rest_duration}
              onChange={(e) =>
                setEditedConfig({
                  ...editedConfig,
                  rest_duration: parseInt(e.target.value),
                })
              }
            />
            <p className="text-sm text-muted-foreground">
              每次休息的时长
            </p>
          </div>

          <Button onClick={handleSaveConfig} disabled={loading}>
            保存配置
          </Button>
        </CardContent>
      </Card>

      {/* 系统信息 */}
      <Card>
        <CardHeader>
          <CardTitle>系统信息</CardTitle>
          <CardDescription>查看系统状态</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">浏览器服务</span>
            <span className={`px-2 py-1 rounded text-xs font-medium ${
              automationStatus?.service_initialized
                ? 'bg-green-100 text-green-700'
                : 'bg-gray-100 text-gray-700'
            }`}>
              {automationStatus?.service_initialized ? '已初始化' : '未初始化'}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">登录状态</span>
            <span className={`px-2 py-1 rounded text-xs font-medium ${
              automationStatus?.is_logged_in
                ? 'bg-green-100 text-green-700'
                : 'bg-gray-100 text-gray-700'
            }`}>
              {automationStatus?.is_logged_in ? '已登录' : '未登录'}
            </span>
          </div>
          {automationStatus?.current_task_id && (
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">当前任务</span>
              <span className="text-sm font-medium">
                #{automationStatus.current_task_id}
              </span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 飞书多维表格配置 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>飞书多维表格</span>
            <Switch
              checked={config?.feishu_enabled || false}
              onCheckedChange={handleToggleFeishu}
              disabled={loading}
            />
          </CardTitle>
          <CardDescription>
            配置飞书多维表格，自动同步已打招呼的候选人信息
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-2">
            <Label htmlFor="feishu_app_id">App ID</Label>
            <Input
              id="feishu_app_id"
              type="text"
              placeholder="cli_xxx"
              value={feishuConfig.feishu_app_id}
              onChange={(e) =>
                setFeishuConfig({
                  ...feishuConfig,
                  feishu_app_id: e.target.value,
                })
              }
            />
            <p className="text-sm text-muted-foreground">
              飞书开放平台应用的 App ID
            </p>
          </div>

          <div className="grid gap-2">
            <Label htmlFor="feishu_app_secret">App Secret</Label>
            <Input
              id="feishu_app_secret"
              type="password"
              placeholder="请输入 App Secret"
              value={feishuConfig.feishu_app_secret}
              onChange={(e) =>
                setFeishuConfig({
                  ...feishuConfig,
                  feishu_app_secret: e.target.value,
                })
              }
            />
            <p className="text-sm text-muted-foreground">
              飞书开放平台应用的 App Secret
            </p>
          </div>

          <div className="grid gap-2">
            <Label htmlFor="feishu_app_token">多维表格 App Token</Label>
            <Input
              id="feishu_app_token"
              type="text"
              placeholder="从多维表格 URL 中获取"
              value={feishuConfig.feishu_app_token}
              onChange={(e) =>
                setFeishuConfig({
                  ...feishuConfig,
                  feishu_app_token: e.target.value,
                })
              }
            />
            <p className="text-sm text-muted-foreground">
              多维表格 URL 中的 app_token 参数
            </p>
          </div>

          <div className="grid gap-2">
            <Label htmlFor="feishu_table_id">数据表 ID</Label>
            <Input
              id="feishu_table_id"
              type="text"
              placeholder="从数据表 URL 中获取"
              value={feishuConfig.feishu_table_id}
              onChange={(e) =>
                setFeishuConfig({
                  ...feishuConfig,
                  feishu_table_id: e.target.value,
                })
              }
            />
            <p className="text-sm text-muted-foreground">
              数据表 URL 中的 table 参数
            </p>
          </div>

          {/* 测试结果提示 */}
          {feishuTestResult && (
            <div
              className={`rounded-lg border p-4 ${
                feishuTestResult.success
                  ? 'border-green-200 bg-green-50'
                  : 'border-red-200 bg-red-50'
              }`}
            >
              <p
                className={`text-sm ${
                  feishuTestResult.success ? 'text-green-800' : 'text-red-800'
                }`}
              >
                {feishuTestResult.message}
              </p>
            </div>
          )}

          <div className="flex gap-2">
            <Button onClick={handleSaveFeishuConfig} disabled={loading}>
              保存配置
            </Button>
            <Button
              variant="outline"
              onClick={handleTestFeishuConnection}
              disabled={loading || feishuTesting}
            >
              {feishuTesting ? '测试中...' : '测试连接'}
            </Button>
            <Button
              variant="outline"
              onClick={handleSyncFeishuFields}
              disabled={loading || feishuSyncing}
            >
              {feishuSyncing ? '同步中...' : '同步字段'}
            </Button>
          </div>

          {/* 配置说明 */}
          <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
            <h4 className="text-sm font-medium text-blue-800 mb-2">配置说明</h4>
            <div className="text-sm text-blue-700 space-y-1">
              <p>1. 在飞书开放平台创建应用并获取 App ID 和 App Secret</p>
              <p>2. 为应用申请「多维表格」相关权限</p>
              <p>3. 创建多维表格并从 URL 中获取 App Token 和 Table ID</p>
              <p>4. 点击「同步字段」自动创建所需的表格字段</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 清除登录确认对话框 */}
      <AlertDialog open={showClearDialog} onOpenChange={setShowClearDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>确认清除登录信息</AlertDialogTitle>
            <AlertDialogDescription>
              确定要清除登录信息吗？清除后需要重新登录才能使用自动化功能。
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>取消</AlertDialogCancel>
            <AlertDialogAction onClick={confirmClearLogin}>确认</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* 二维码登录对话框 */}
      <Dialog open={showQrcodeDialog} onOpenChange={handleCloseQrcodeDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>扫码登录</DialogTitle>
            <DialogDescription>
              使用 Boss 直聘 APP 扫描二维码完成登录
            </DialogDescription>
          </DialogHeader>
          <div className="flex flex-col items-center justify-center space-y-4 py-6">
            {qrcodeUrl ? (
              <>
                <div className="border-2 border-gray-200 rounded-lg p-4 bg-white">
                  <img
                    src={qrcodeUrl}
                    alt="登录二维码"
                    className="w-64 h-64 object-contain"
                    onError={() => {
                      console.error('二维码加载失败');
                      toast.error('二维码加载失败');
                    }}
                  />
                </div>
                {checkingLogin && (
                  <div className="flex flex-col items-center space-y-2">
                    <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                      <span>等待扫码登录...</span>
                    </div>
                    {refreshCount > 0 && (
                      <div className="text-xs text-muted-foreground">
                        已自动刷新 {refreshCount} 次
                      </div>
                    )}
                  </div>
                )}
              </>
            ) : (
              <div className="flex items-center justify-center w-64 h-64 border-2 border-dashed border-gray-300 rounded-lg">
                <span className="text-muted-foreground">加载二维码中...</span>
              </div>
            )}
            <div className="text-xs text-center text-muted-foreground space-y-1">
              <p>1. 打开 Boss 直聘 APP</p>
              <p>2. 点击「扫一扫」功能</p>
              <p>3. 扫描上方二维码</p>
              <p>4. 在 APP 中确认登录</p>
            </div>
          </div>
          <div className="flex justify-center">
            <Button variant="outline" onClick={handleCloseQrcodeDialog}>
              取消登录
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
