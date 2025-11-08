/**
 * 自动化向导页面 - 一站式配置和启动自动化任务
 */
import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Zap, Monitor, CheckCircle2, Settings2, PlayCircle, Loader2, Briefcase, X, Save, ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';

import { useAutomation } from '@/hooks/useAutomation';
import { useJobs } from '@/hooks/useJobs';
import { useAutomationTemplates } from '@/hooks/useAutomationTemplates';
import { useAccounts } from '@/hooks/useAccounts';
import type { Job, GreetingStatus, GreetingLogEntry } from '@/types';
import type { UserAccount } from '@/types/account';
import { FilterConfig } from '@/components/FilterConfig';
import { type FilterOptions, DEFAULT_FILTERS } from '@/types/filters';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Separator } from '@/components/ui/separator';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';

type WizardStep = 'browser' | 'login' | 'job-select' | 'configure' | 'confirm';

export default function AutomationWizard() {
  const navigate = useNavigate();
  const { initBrowser, getQRCode, checkLogin, getAvailableJobs, selectJob, applyFilters } = useAutomation();
  const { getJobs } = useJobs();
  const { createTemplate } = useAutomationTemplates();
  const { getAccounts, getCurrentAccount } = useAccounts();

  // 步骤状态
  const [currentStep, setCurrentStep] = useState<WizardStep>('browser');

  // 模板保存相关
  const [saveTemplateDialogOpen, setSaveTemplateDialogOpen] = useState(false);
  const [templateName, setTemplateName] = useState('');
  const [templateDescription, setTemplateDescription] = useState('');
  const [savingTemplate, setSavingTemplate] = useState(false);

  // 浏览器配置
  const [showBrowser, setShowBrowser] = useState(false);
  const [browserInitializing, setBrowserInitializing] = useState(false);

  // 账号相关状态
  const [availableAccounts, setAvailableAccounts] = useState<UserAccount[]>([]);
  const [selectedAccountId, setSelectedAccountId] = useState<number | null>(null);
  const [useExistingAccount, setUseExistingAccount] = useState(false);

  // 登录状态
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userInfo, setUserInfo] = useState<any>(null);
  const [qrCode, setQrCode] = useState<string>('');
  const [checkingLogin, setCheckingLogin] = useState(false);
  const [qrRefreshCount, setQrRefreshCount] = useState(0); // 二维码刷新次数
  const [qrElapsedTime, setQrElapsedTime] = useState(0); // 二维码已等待时间（秒）
  const [qrCodeExpired, setQrCodeExpired] = useState(false); // 二维码是否过期

  // 职位选择状态
  const [availableJobs, setAvailableJobs] = useState<Array<{ value: string; label: string }>>([]);
  const [selectedJobValue, setSelectedJobValue] = useState<string>('');
  const [loadingJobs, setLoadingJobs] = useState(false);
  const [selectingJob, setSelectingJob] = useState(false);

  // 配置状态
  const [selectedJob, setSelectedJob] = useState<string>('');
  const [maxContacts, setMaxContacts] = useState<number | ''>(10);
  const [filters, setFilters] = useState<FilterOptions>(DEFAULT_FILTERS);

  // 数据加载
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);

  // 打招呼任务状态
  const [greetingStarted, setGreetingStarted] = useState(false);
  const [greetingStatus, setGreetingStatus] = useState<GreetingStatus | null>(null);
  const [greetingLogs, setGreetingLogs] = useState<GreetingLogEntry[]>([]);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // 期望职位匹配相关状态
  const [expectedPositions, setExpectedPositions] = useState<string[]>([]);
  const [positionInput, setPositionInput] = useState('');

  // 筛选应用
  const [applyingFilters, setApplyingFilters] = useState(false);

  /**
   * 初始化浏览器
   */
  const handleInitBrowser = async () => {
    setBrowserInitializing(true);
    try {
      // 先加载账号列表
      try {
        const accounts = await getAccounts();
        setAvailableAccounts(accounts);

        // 尝试获取当前账号
        const currentAccount = await getCurrentAccount();
        if (currentAccount) {
          setSelectedAccountId(currentAccount.id);
        }
      } catch (error) {
        console.error('加载账号列表失败:', error);
        // 继续执行，即使加载账号列表失败
      }

      const result = await initBrowser(!showBrowser);

      if (result.success) {
        toast.success(result.message);

        // 进入登录步骤，让用户选择账号或扫码登录
        setCurrentStep('login');

        // 如果已经有选中的账号，尝试使用该账号登录
        if (selectedAccountId) {
          setCheckingLogin(true);
          toast.info('正在检查登录状态...');

          try {
            const loginResult = await checkLogin();

            if (loginResult.logged_in) {
              // 已登录,进入职位选择步骤
              setIsLoggedIn(true);
              setUserInfo(loginResult.user_info);
              setCurrentStep('job-select');
              toast.success(`欢迎回来,${loginResult.user_info?.showName || '用户'}!`);
              // 加载可用职位
              await loadAvailableJobs();
            }
          } catch (error) {
            console.error('检查登录状态失败:', error);
          } finally {
            setCheckingLogin(false);
          }
        }
      }
    } catch (error) {
      console.error('浏览器初始化失败:', error);
      toast.error('浏览器初始化失败');
    } finally {
      setBrowserInitializing(false);
    }
  };

  /**
   * 选择账号并使用其登录状态
   */
  const handleSelectExistingAccount = async () => {
    if (!selectedAccountId) {
      toast.error('请选择账号');
      return;
    }

    setCheckingLogin(true);
    setUseExistingAccount(true);

    try {
      // 找到选中账号的com_id
      const selectedAccount = availableAccounts.find(acc => acc.id === selectedAccountId);
      if (!selectedAccount) {
        toast.error('未找到选中的账号');
        return;
      }

      // 使用选中账号的com_id初始化浏览器（加载该账号的cookies）
      const result = await initBrowser(!showBrowser, selectedAccount.com_id);

      if (result.success) {
        toast.success(result.message);

        // 检查登录状态
        const loginResult = await checkLogin();

        if (loginResult.logged_in) {
          setIsLoggedIn(true);
          setUserInfo(loginResult.user_info);
          setCurrentStep('job-select');
          toast.success(`使用账号 ${loginResult.user_info?.showName || '用户'} 登录成功！`);
          // 加载可用职位
          await loadAvailableJobs();
        } else {
          toast.error('该账号登录状态已过期，请重新扫码登录');
          setUseExistingAccount(false);
          await handleGetQRCode();
        }
      }
    } catch (error) {
      console.error('使用已有账号失败:', error);
      toast.error('使用已有账号失败');
      setUseExistingAccount(false);
    } finally {
      setCheckingLogin(false);
    }
  };

  /**
   * 获取二维码
   */
  const handleGetQRCode = async () => {
    setCheckingLogin(true);
    setUseExistingAccount(false);
    setSelectedAccountId(null);

    try {
      const qrResult = await getQRCode();
      if (qrResult.qrcode) {
        setQrCode(qrResult.qrcode);
        // 开始轮询登录状态
        startLoginPolling();
      } else if (qrResult.message === '已登录，无需扫码') {
        // 已经登录，获取用户信息
        const loginResult = await checkLogin();
        if (loginResult.logged_in) {
          setIsLoggedIn(true);
          setUserInfo(loginResult.user_info);
          setCurrentStep('job-select');
          toast.success('检测到已登录状态');
          // 加载可用职位
          await loadAvailableJobs();
        }
      }
    } catch (error) {
      console.error('获取二维码失败:', error);
      toast.error('获取二维码失败');
    } finally {
      setCheckingLogin(false);
    }
  };

  /**
   * 重新登录 - 重置状态并重新获取二维码
   */
  const handleRetryLogin = async () => {
    console.log('🔄 重新登录...');
    setQrCodeExpired(false);
    setQrRefreshCount(0);
    setQrElapsedTime(0);
    await handleGetQRCode();
  };

  /**
   * 返回账号选择界面
   */
  const handleBackToAccountSelect = () => {
    // 清空二维码状态
    setQrCode('');
    setQrCodeExpired(false);
    setQrRefreshCount(0);
    setQrElapsedTime(0);
    setCheckingLogin(false);
    setUseExistingAccount(false);

    toast.info('已返回账号选择');
  };

  /**
   * 轮询登录状态
   */
  const startLoginPolling = () => {
    let localRefreshCount = 0; // 二维码刷新次数计数器
    const MAX_QR_REFRESH_COUNT = 5; // 最大刷新次数
    const startTime = Date.now(); // 记录开始时间

    // 重置UI状态
    setQrRefreshCount(0);
    setQrElapsedTime(0);
    setQrCodeExpired(false);

    // 计时器 - 每秒更新一次显示的时间
    const timerInterval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTime) / 1000);
      setQrElapsedTime(elapsed);
    }, 1000);

    // 登录状态轮询 - 每2秒检查一次
    const loginInterval = setInterval(async () => {
      try {
        const result = await checkLogin();
        if (result.logged_in) {
          clearInterval(loginInterval);
          clearInterval(qrRefreshInterval);
          clearInterval(timerInterval);
          setIsLoggedIn(true);
          setUserInfo(result.user_info);
          setCurrentStep('job-select');
          toast.success('登录成功！');
          // 加载可用职位
          await loadAvailableJobs();
        }
      } catch (error) {
        // 继续轮询
      }
    }, 2000);

    // 二维码刷新轮询 - 每30秒刷新一次二维码（后端会自动检测过期并刷新）
    const qrRefreshInterval = setInterval(async () => {
      // 先检查是否已经达到最大刷新次数
      if (localRefreshCount >= MAX_QR_REFRESH_COUNT) {
        console.error('❌ 二维码刷新超时：已达到最大刷新次数 (5次)');
        clearInterval(loginInterval);
        clearInterval(qrRefreshInterval);
        clearInterval(timerInterval);
        setQrCodeExpired(true); // 标记二维码已过期
        toast.error('二维码刷新超时，请点击重新登录按钮');
        return;
      }

      localRefreshCount++;
      setQrRefreshCount(localRefreshCount); // 更新UI显示的刷新次数
      console.log(`🔄 轮询刷新二维码... (第 ${localRefreshCount}/${MAX_QR_REFRESH_COUNT} 次)`);

      try {
        const qrResult = await getQRCode();
        if (qrResult.success && qrResult.qrcode) {
          // 更新二维码显示
          setQrCode(qrResult.qrcode);
          console.log(`✅ 二维码已更新 (第 ${localRefreshCount} 次)`);
        } else {
          console.warn(`⚠️ 二维码刷新失败 (第 ${localRefreshCount} 次):`, qrResult.message);
        }
      } catch (error) {
        console.error(`❌ 刷新二维码出错 (第 ${localRefreshCount} 次):`, error);
        // 继续轮询，直到达到最大次数
      }
    }, 30000); // 30秒刷新一次

    // 3分钟后停止轮询（作为备用超时机制）
    setTimeout(() => {
      clearInterval(loginInterval);
      clearInterval(qrRefreshInterval);
      clearInterval(timerInterval);
      if (localRefreshCount >= MAX_QR_REFRESH_COUNT) {
        console.log('⏱️ 轮询已达到最大次数限制');
      } else {
        console.log('⏱️ 轮询已达到时间限制 (3分钟)');
      }
    }, 180000);
  };

  /**
   * 加载可用职位列表
   */
  const loadAvailableJobs = async () => {
    setLoadingJobs(true);
    try {
      const result = await getAvailableJobs();
      if (result.success) {
        setAvailableJobs(result.jobs);
        if (result.jobs.length > 0) {
          setSelectedJobValue(result.jobs[0].value);
        }
        toast.success(`成功加载 ${result.jobs.length} 个职位`);
      } else {
        toast.error(result.message || '获取职位列表失败');
      }
    } catch (error) {
      console.error('加载职位列表失败:', error);
      toast.error('加载职位列表失败');
    } finally {
      setLoadingJobs(false);
    }
  };

  /**
   * 选择职位并进入配置步骤
   */
  const handleSelectJob = async () => {
    if (!selectedJobValue) {
      toast.error('请选择职位');
      return;
    }

    setSelectingJob(true);
    try {
      const result = await selectJob(selectedJobValue);
      if (result.success) {
        toast.success('职位选择成功');
        setSelectedJob(selectedJobValue); // 设置选中的职位ID
        setCurrentStep('configure');
        // 加载职位数据
        await loadData();
      } else {
        toast.error(result.message || '职位选择失败');
      }
    } catch (error) {
      console.error('选择职位失败:', error);
      toast.error('选择职位失败');
    } finally {
      setSelectingJob(false);
    }
  };

  /**
   * 加载职位数据
   */
  const loadData = async () => {
    setLoading(true);
    try {
      const jobsResult = await getJobs();

      if (jobsResult.success) {
        setJobs(jobsResult.jobs);
      }
    } catch (error) {
      console.error('加载数据失败:', error);
      toast.error('加载数据失败');
    } finally {
      setLoading(false);
    }
  };


  /**
   * 应用筛选条件到浏览器
   */
  const handleApplyFilters = async () => {
    setApplyingFilters(true);
    try {
      toast.info('正在浏览器中应用筛选条件...');
      const filterResult = await applyFilters(filters);

      if (filterResult.success) {
        toast.success(`已应用 ${filterResult.applied_count} 项筛选条件`);
        // 筛选成功后进入确认步骤
        setCurrentStep('confirm');
      } else {
        toast.error('筛选条件应用失败，请重试');
      }
    } catch (filterError) {
      console.error('应用筛选条件失败:', filterError);
      toast.error('应用筛选条件失败');
    } finally {
      setApplyingFilters(false);
    }
  };

  /**
   * 添加期望职位
   */
  const handleAddPosition = () => {
    const trimmed = positionInput.trim();
    if (trimmed && !expectedPositions.includes(trimmed)) {
      setExpectedPositions([...expectedPositions, trimmed]);
      setPositionInput('');
    } else if (expectedPositions.includes(trimmed)) {
      toast.warning('该职位已添加');
    }
  };

  /**
   * 删除期望职位
   */
  const handleRemovePosition = (index: number) => {
    setExpectedPositions(expectedPositions.filter((_, i) => i !== index));
  };

  /**
   * 开始打招呼任务
   */
  const handleStartAutomation = async () => {
    try {
      // 验证输入
      const targetCount = maxContacts === '' ? 10 : maxContacts;
      if (targetCount < 1 || targetCount > 300) {
        toast.error('打招呼数量必须在 1-300 之间');
        return;
      }

      toast.info('正在启动打招呼任务...');

      // 直接调用 greeting API
      const response = await fetch('http://localhost:27421/api/greeting/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          target_count: targetCount,
          expected_positions: expectedPositions
        })
      });

      const data = await response.json();

      if (response.ok) {
        toast.success('打招呼任务已启动！');
        setGreetingStarted(true);

        // 开始轮询状态
        startPolling();
      } else {
        // 处理各种错误格式
        let errorMessage = '启动失败';
        if (typeof data.detail === 'string') {
          errorMessage = data.detail;
        } else if (Array.isArray(data.detail)) {
          // FastAPI验证错误格式
          errorMessage = data.detail.map((err: any) => err.msg).join(', ');
        } else if (data.message) {
          errorMessage = data.message;
        }
        toast.error(errorMessage);
      }
    } catch (error) {
      console.error('启动任务失败:', error);
      toast.error('启动失败，请检查后端服务');
    }
  };

  /**
   * 保存为模板
   */
  const handleSaveTemplate = async () => {
    if (!templateName.trim()) {
      toast.error('请输入模板名称');
      return;
    }

    setSavingTemplate(true);
    try {
      await createTemplate({
        name: templateName.trim(),
        description: templateDescription.trim() || undefined,
        account_id: userInfo?.com_id,
        headless: !showBrowser,
        job_id: selectedJobValue,
        job_name: availableJobs.find(j => j.value === selectedJobValue)?.label,
        filters: filters,
        greeting_count: maxContacts === '' ? 10 : maxContacts,
        expected_positions: expectedPositions.length > 0 ? expectedPositions : undefined,
      });

      toast.success('模板保存成功！');
      setSaveTemplateDialogOpen(false);
      setTemplateName('');
      setTemplateDescription('');
    } catch (error) {
      console.error('保存模板失败:', error);
      toast.error(error instanceof Error ? error.message : '保存模板失败');
    } finally {
      setSavingTemplate(false);
    }
  };

  /**
   * 开始轮询打招呼状态
   */
  const startPolling = () => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }

    pollingIntervalRef.current = setInterval(async () => {
      try {
        // 获取状态
        const statusRes = await fetch('http://localhost:27421/api/greeting/status');
        const statusData = await statusRes.json();
        setGreetingStatus(statusData);

        // 获取日志
        const logsRes = await fetch('http://localhost:27421/api/greeting/logs?last_n=100');
        const logsData = await logsRes.json();
        setGreetingLogs(logsData.logs);

        // 如果任务完成或出错，停止轮询并重置按钮状态
        if (statusData.status !== 'running') {
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }
          // 重置按钮状态，使其可以再次点击
          setGreetingStarted(false);
        }
      } catch (error) {
        console.error('轮询失败:', error);
      }
    }, 1000);
  };

  // 清理轮询
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  // 从模板加载配置
  useEffect(() => {
    const templateData = sessionStorage.getItem('selectedTemplate');
    if (templateData) {
      try {
        const template = JSON.parse(templateData);

        // 应用模板配置
        setShowBrowser(!template.headless);
        if (template.filters) {
          setFilters(template.filters);
        }
        if (template.greeting_count) {
          setMaxContacts(template.greeting_count);
        }
        if (template.expected_positions && template.expected_positions.length > 0) {
          setExpectedPositions(template.expected_positions);
        }
        if (template.job_id) {
          setSelectedJobValue(template.job_id);
        }

        // 清除sessionStorage
        sessionStorage.removeItem('selectedTemplate');

        toast.success(`已加载模板：${template.name}`);
      } catch (error) {
        console.error('加载模板失败:', error);
        toast.error('加载模板失败');
      }
    }
  }, []);

  /**
   * 渲染浏览器配置步骤
   */
  const renderBrowserStep = () => (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Monitor className="h-6 w-6 text-primary" />
          步骤 1: 浏览器配置
        </CardTitle>
        <CardDescription>
          选择浏览器显示模式，然后开始初始化
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          <div className="flex items-start space-x-3 p-4 border rounded-lg">
            <Checkbox
              id="showBrowser"
              checked={showBrowser}
              onCheckedChange={(checked) => setShowBrowser(checked as boolean)}
            />
            <div className="flex-1">
              <Label
                htmlFor="showBrowser"
                className="text-sm font-medium leading-none cursor-pointer"
              >
                显示浏览器窗口
              </Label>
              <p className="text-sm text-muted-foreground mt-1.5">
                勾选此选项将显示浏览器窗口，便于调试和观察执行过程。
                建议首次使用时勾选，熟悉后可取消以提高效率。
              </p>
            </div>
          </div>

          <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg">
            <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
              💡 提示
            </h4>
            <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
              <li>• 显示窗口：可以看到浏览器操作过程，适合调试</li>
              <li>• 隐藏窗口：后台静默运行，节省资源，适合正式使用</li>
              <li>• 初始化后无法更改，如需修改请重新开始</li>
            </ul>
          </div>
        </div>

        <Button
          onClick={handleInitBrowser}
          disabled={browserInitializing}
          className="w-full"
          size="lg"
        >
          {browserInitializing ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              正在初始化浏览器...
            </>
          ) : (
            <>
              <Zap className="mr-2 h-4 w-4" />
              开始初始化
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );

  /**
   * 渲染登录步骤
   */
  const renderLoginStep = () => (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Zap className="h-6 w-6 text-primary" />
          步骤 2: 登录账号
        </CardTitle>
        <CardDescription>
          {availableAccounts.length > 0
            ? '选择已有账号或扫码登录新账号'
            : '使用 Boss 直聘 APP 扫描二维码登录'}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* 账号选择区域 */}
        {availableAccounts.length > 0 && !qrCode && (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="account-select">选择已登录的账号</Label>
              <Select
                value={selectedAccountId?.toString() || ''}
                onValueChange={(value) => setSelectedAccountId(Number(value))}
              >
                <SelectTrigger id="account-select">
                  <SelectValue placeholder="请选择账号" />
                </SelectTrigger>
                <SelectContent>
                  {availableAccounts.map((account) => (
                    <SelectItem key={account.id} value={account.id.toString()}>
                      <div className="flex items-center gap-2">
                        {account.avatar && (
                          <img
                            src={account.avatar}
                            alt={account.show_name}
                            className="w-6 h-6 rounded-full"
                          />
                        )}
                        <span>{account.show_name}</span>
                        <span className="text-muted-foreground text-sm">
                          ({account.company_short_name || account.company_name})
                        </span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <Button
              onClick={handleSelectExistingAccount}
              disabled={!selectedAccountId || checkingLogin}
              className="w-full"
            >
              {checkingLogin ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  正在加载账号...
                </>
              ) : (
                '使用选中账号'
              )}
            </Button>

            <Separator />

            <div className="text-center">
              <Button
                variant="outline"
                onClick={handleGetQRCode}
                disabled={checkingLogin}
                className="w-full"
              >
                或者扫码登录新账号
              </Button>
            </div>
          </div>
        )}

        {/* 二维码登录区域 */}
        {checkingLogin && !qrCode && !useExistingAccount ? (
          <div className="flex flex-col items-center justify-center py-12">
            <Loader2 className="h-12 w-12 animate-spin text-muted-foreground mb-4" />
            <p className="text-muted-foreground">正在获取二维码...</p>
          </div>
        ) : qrCode ? (
          <div className="flex flex-col items-center space-y-4">
            {/* 二维码容器 - 支持遮罩 */}
            <div className="relative">
              <img
                src={qrCode}
                alt="登录二维码"
                className="w-64 h-64 border-2 border-gray-200 rounded-lg"
              />
              {/* 二维码过期遮罩 */}
              {qrCodeExpired && (
                <div className="absolute inset-0 bg-black/60 backdrop-blur-sm rounded-lg flex flex-col items-center justify-center gap-4">
                  <div className="text-white text-center">
                    <p className="text-lg font-semibold mb-2">二维码已过期</p>
                    <p className="text-sm text-gray-300">已达到最大刷新次数 (5次)</p>
                  </div>
                  <Button
                    onClick={handleRetryLogin}
                    variant="default"
                    className="bg-white text-black hover:bg-gray-100"
                  >
                    重新登录
                  </Button>
                </div>
              )}
            </div>
            <p className="text-sm text-muted-foreground text-center">
              请使用 Boss 直聘 APP 扫描二维码登录
            </p>
            {!qrCodeExpired && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                等待扫码...
              </div>
            )}
            {/* 显示刷新次数和计时 */}
            <div className="flex flex-col items-center gap-2 pt-2 border-t border-gray-200 w-full">
              <div className="flex items-center gap-4 text-xs text-muted-foreground">
                <div className="flex items-center gap-1">
                  <span className="font-medium">已刷新:</span>
                  <span className="font-mono">{qrRefreshCount}/5 次</span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="font-medium">已等待:</span>
                  <span className="font-mono">
                    {Math.floor(qrElapsedTime / 60)}:{String(qrElapsedTime % 60).padStart(2, '0')}
                  </span>
                </div>
              </div>
              {qrRefreshCount > 0 && !qrCodeExpired && (
                <div className="text-xs text-blue-600">
                  二维码每30秒自动刷新，最多刷新5次
                </div>
              )}
              {qrCodeExpired && (
                <div className="text-xs text-red-600">
                  二维码刷新超时，请点击上方按钮重新登录
                </div>
              )}
            </div>

            {/* 返回按钮 */}
            {availableAccounts.length > 0 && (
              <div className="w-full pt-4 border-t border-gray-200">
                <Button
                  variant="outline"
                  onClick={handleBackToAccountSelect}
                  className="w-full"
                >
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  返回选择账号
                </Button>
              </div>
            )}
          </div>
        ) : null}
      </CardContent>
    </Card>
  );

  /**
   * 渲染职位选择步骤
   */
  const renderJobSelectStep = () => (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Briefcase className="h-6 w-6 text-primary" />
          步骤 3: 选择招聘职位
        </CardTitle>
        <CardDescription>
          选择要为其推荐候选人的招聘职位
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {loadingJobs ? (
          <div className="flex flex-col items-center justify-center py-12">
            <Loader2 className="h-12 w-12 animate-spin text-muted-foreground mb-4" />
            <p className="text-muted-foreground">正在加载职位列表...</p>
          </div>
        ) : availableJobs.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12">
            <p className="text-muted-foreground mb-4">暂无可用职位</p>
            <Button onClick={loadAvailableJobs} variant="outline">
              重新加载
            </Button>
          </div>
        ) : (
          <>
            <div className="space-y-4">
              <Label htmlFor="job-select">可用职位</Label>
              <Select
                value={selectedJobValue}
                onValueChange={(value) => setSelectedJobValue(value)}
              >
                <SelectTrigger id="job-select">
                  <SelectValue placeholder="选择职位" />
                </SelectTrigger>
                <SelectContent>
                  {availableJobs.map((job) => (
                    <SelectItem key={job.value} value={job.value}>
                      {job.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <p className="text-sm text-muted-foreground">
                找到 {availableJobs.length} 个可用职位
              </p>
            </div>

            <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg">
              <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
                💡 提示
              </h4>
              <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
                <li>• 选择的职位将用于在推荐牛人页面筛选候选人</li>
                <li>• 系统会根据选择的职位推荐相关候选人</li>
                <li>• 确保选择正确的职位以获得最佳推荐效果</li>
              </ul>
            </div>

            <div className="flex justify-end gap-4">
              <Button
                variant="outline"
                onClick={() => setCurrentStep('login')}
                disabled={selectingJob}
              >
                返回登录
              </Button>
              <Button
                onClick={handleSelectJob}
                disabled={!selectedJobValue || selectingJob}
              >
                {selectingJob ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    正在选择...
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="mr-2 h-4 w-4" />
                    确认选择
                  </>
                )}
              </Button>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );

  /**
   * 渲染配置步骤
   */
  const renderConfigureStep = () => (
    <div className="max-w-4xl mx-auto space-y-6">
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-4">
            {userInfo?.avatar && (
              <img
                src={userInfo.avatar}
                alt={userInfo.showName}
                className="w-12 h-12 rounded-full object-cover"
              />
            )}
            <div>
              <p className="font-medium text-lg">{userInfo?.showName || '未知用户'}</p>
              <p className="text-sm text-muted-foreground">
                {userInfo?.brandName || '未知公司'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings2 className="h-6 w-6 text-primary" />
            步骤 4: 配置筛选条件
          </CardTitle>
          <CardDescription>
            设置候选人筛选条件以精准匹配目标人才
          </CardDescription>
        </CardHeader>
        <CardContent>
          <FilterConfig filters={filters} onChange={setFilters} />
        </CardContent>
      </Card>

      <div className="flex justify-between gap-4">
        <Button
          variant="outline"
          onClick={() => setCurrentStep('job-select')}
          disabled={applyingFilters}
        >
          返回职位选择
        </Button>
        <Button
          onClick={handleApplyFilters}
          disabled={!selectedJob || jobs.length === 0 || applyingFilters}
        >
          {applyingFilters ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              正在应用筛选条件...
            </>
          ) : (
            '应用筛选并继续'
          )}
        </Button>
      </div>
    </div>
  );

  /**
   * 渲染确认步骤
   */
  const renderConfirmStep = () => {
    // 统计设置的筛选条件数量
    const activeFiltersCount = Object.entries(filters).filter(([key, value]) => {
      if (key === 'age') return value !== null;
      if (Array.isArray(value)) return value.length > 0;
      return value && value !== '不限';
    }).length;

    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PlayCircle className="h-6 w-6 text-primary" />
              步骤 5: 确认并启动
            </CardTitle>
            <CardDescription>
              请确认以下配置无误后，点击启动按钮
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <div>
                <Label className="text-muted-foreground">浏览器显示</Label>
                <p className="font-medium">
                  {showBrowser ? '显示窗口' : '后台运行（隐藏窗口）'}
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="maxContacts">需要打招呼的数量</Label>
                <p className="text-sm text-muted-foreground">
                  成功打招呼达到此数量后停止（不包括跳过的候选人）
                </p>
                <Input
                  id="maxContacts"
                  type="number"
                  min="1"
                  max="300"
                  value={maxContacts}
                  onChange={(e) => {
                    const value = e.target.value;
                    if (value === '') {
                      setMaxContacts('');
                    } else {
                      const num = parseInt(value);
                      if (!isNaN(num)) {
                        setMaxContacts(num);
                      }
                    }
                  }}
                  onBlur={(e) => {
                    // 失去焦点时，如果为空则设置为默认值10
                    if (e.target.value === '') {
                      setMaxContacts(10);
                    }
                  }}
                  className="max-w-xs"
                />
                <p className="text-sm text-muted-foreground">
                  最多可设置 300 人，建议分批次进行，避免触发平台限制
                </p>
              </div>

              {/* 期望职位匹配（可选） */}
              <div className="space-y-2">
                <Label>期望职位匹配（可选）</Label>
                <p className="text-sm text-muted-foreground">
                  只向期望职位包含以下关键词的候选人打招呼
                </p>

                {/* 输入框和添加按钮 */}
                <div className="flex gap-2">
                  <Input
                    placeholder="输入职位关键词，如：Java、产品经理"
                    value={positionInput}
                    onChange={(e) => setPositionInput(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        handleAddPosition();
                      }
                    }}
                    className="flex-1"
                  />
                  <Button
                    type="button"
                    onClick={handleAddPosition}
                    variant="outline"
                  >
                    添加
                  </Button>
                </div>

                {/* 标签列表展示 */}
                {expectedPositions.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    {expectedPositions.map((pos, index) => (
                      <Badge
                        key={index}
                        variant="secondary"
                        className="px-3 py-1 text-sm"
                      >
                        {pos}
                        <X
                          className="ml-1 h-3 w-3 cursor-pointer hover:text-red-600"
                          onClick={() => handleRemovePosition(index)}
                        />
                      </Badge>
                    ))}
                  </div>
                )}
              </div>

              <div>
                <Label className="text-muted-foreground">筛选条件</Label>
                <p className="font-medium">
                  已设置 {activeFiltersCount} 项筛选条件
                </p>

                {/* 显示部分关键筛选 */}
                <div className="mt-2 space-y-1">
                  {filters.age && (
                    <p className="text-sm text-muted-foreground">
                      • 年龄: {filters.age.min} - {filters.age.max || '不限'} 岁
                    </p>
                  )}
                  {filters.activity && filters.activity !== '不限' && (
                    <p className="text-sm text-muted-foreground">
                      • 活跃度: {filters.activity}
                    </p>
                  )}
                  {filters.jobHoppingFrequency && filters.jobHoppingFrequency !== '不限' && (
                    <p className="text-sm text-muted-foreground">
                      • 跳槽频率: {filters.jobHoppingFrequency}
                    </p>
                  )}
                  {filters.salary && filters.salary !== '不限' && (
                    <p className="text-sm text-muted-foreground">
                      • 薪资待遇: {filters.salary}
                    </p>
                  )}
                  {filters.gender && filters.gender.length > 0 && (
                    <p className="text-sm text-muted-foreground">
                      • 性别: {filters.gender.join('、')}
                    </p>
                  )}
                  {filters.experience && filters.experience.length > 0 && (
                    <p className="text-sm text-muted-foreground">
                      • 经验要求: {filters.experience.join('、')}
                    </p>
                  )}
                  {filters.education && filters.education.length > 0 && (
                    <p className="text-sm text-muted-foreground">
                      • 学历要求: {filters.education.join('、')}
                    </p>
                  )}
                  {filters.major && filters.major.length > 0 && (
                    <p className="text-sm text-muted-foreground">
                      • 专业: {filters.major.join('、')}
                    </p>
                  )}
                  {filters.school && filters.school.length > 0 && (
                    <p className="text-sm text-muted-foreground">
                      • 院校: {filters.school.join('、')}
                    </p>
                  )}
                  {filters.notRecentlyViewed && filters.notRecentlyViewed.length > 0 && (
                    <p className="text-sm text-muted-foreground">
                      • 近期没有看过: {filters.notRecentlyViewed.join('、')}
                    </p>
                  )}
                  {filters.resumeExchange && filters.resumeExchange.length > 0 && (
                    <p className="text-sm text-muted-foreground">
                      • 与同事交换简历: {filters.resumeExchange.join('、')}
                    </p>
                  )}
                  {filters.jobIntention && filters.jobIntention.length > 0 && (
                    <p className="text-sm text-muted-foreground">
                      • 求职意向: {filters.jobIntention.join('、')}
                    </p>
                  )}
                  {filters.keywords && filters.keywords.length > 0 && (
                    <p className="text-sm text-muted-foreground">
                      • 关键词: {filters.keywords.join('、')}
                    </p>
                  )}
                </div>
              </div>

              <div className="pt-4 border-t">
                <Label className="text-muted-foreground">预计操作</Label>
                <p className="font-medium">
                  筛选条件已在浏览器中应用，将自动向符合条件的候选人发送问候
                </p>
                <p className="text-xs text-muted-foreground mt-2">
                  💡 提示：如果返回修改筛选条件，需要重新应用
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <Button
                variant="outline"
                onClick={() => setCurrentStep('configure')}
                disabled={greetingStarted}
              >
                返回修改
              </Button>
              <Button
                variant="outline"
                onClick={() => setSaveTemplateDialogOpen(true)}
                disabled={greetingStarted}
              >
                <Save className="mr-2 h-4 w-4" />
                保存为模板
              </Button>
              <Button
                onClick={handleStartAutomation}
                disabled={greetingStarted}
                className="flex-1"
              >
                {greetingStarted ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    任务进行中...
                  </>
                ) : (
                  <>
                    <PlayCircle className="mr-2 h-4 w-4" />
                    开始打招呼
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* 进度显示 */}
        {greetingStarted && greetingStatus && (
          <>
            <Card>
              <CardHeader>
                <CardTitle>执行进度</CardTitle>
                <CardDescription>
                  {greetingStatus.progress?.toFixed(1)}% 完成
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div
                    className="bg-blue-600 h-2.5 rounded-full transition-all"
                    style={{ width: `${greetingStatus.progress || 0}%` }}
                  ></div>
                </div>
                <p className="text-sm text-muted-foreground mt-2">
                  {greetingStatus.status === 'running' && `正在处理第 ${greetingStatus.current_index} 个候选人...`}
                  {greetingStatus.status === 'completed' && `✅ 任务完成！成功 ${greetingStatus.success_count} 个，失败 ${greetingStatus.failed_count} 个${greetingStatus.skipped_count > 0 ? `，跳过 ${greetingStatus.skipped_count} 个` : ''}`}
                  {greetingStatus.status === 'idle' && '等待开始...'}
                </p>

                {/* 统计信息 */}
                <div className="grid grid-cols-3 gap-4 mt-4">
                  <div>
                    <p className="text-sm text-muted-foreground">成功数</p>
                    <p className="text-2xl font-bold text-green-600">{greetingStatus.success_count}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">失败数</p>
                    <p className="text-2xl font-bold text-red-600">{greetingStatus.failed_count}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">跳过数</p>
                    <p className="text-2xl font-bold text-yellow-600">{greetingStatus.skipped_count || 0}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* 日志显示 */}
            <Card>
              <CardHeader>
                <CardTitle>运行日志</CardTitle>
                <CardDescription>实时显示任务执行日志</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-96 overflow-y-auto bg-gray-50 rounded-lg p-4 font-mono text-sm space-y-1">
                  {greetingLogs.length === 0 ? (
                    <p className="text-muted-foreground text-center py-8">
                      暂无日志
                    </p>
                  ) : (
                    greetingLogs.map((log, index) => (
                      <div
                        key={index}
                        className="flex items-start gap-2 py-1 border-b border-gray-200 last:border-0"
                      >
                        <span className="text-xs text-gray-500 w-24 flex-shrink-0">
                          {new Date(log.timestamp).toLocaleTimeString()}
                        </span>
                        <span className="flex-1">{log.message}</span>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </>
        )}

        {/* 保存模板对话框 */}
        <Dialog open={saveTemplateDialogOpen} onOpenChange={setSaveTemplateDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>保存为模板</DialogTitle>
              <DialogDescription>
                保存当前配置为模板，下次可以快速复用
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="template-name">模板名称 *</Label>
                <Input
                  id="template-name"
                  placeholder="如：Java开发-活跃候选人"
                  value={templateName}
                  onChange={(e) => setTemplateName(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="template-description">模板描述（可选）</Label>
                <Textarea
                  id="template-description"
                  placeholder="描述此模板的用途或特点..."
                  value={templateDescription}
                  onChange={(e) => setTemplateDescription(e.target.value)}
                  rows={3}
                />
              </div>
              <div className="text-sm text-muted-foreground">
                <p>将保存以下配置：</p>
                <ul className="list-disc list-inside mt-2 space-y-1">
                  <li>浏览器显示模式：{showBrowser ? '显示窗口' : '后台运行'}</li>
                  <li>职位：{availableJobs.find(j => j.value === selectedJobValue)?.label}</li>
                  <li>筛选条件：{Object.entries(filters).filter(([key, value]) => {
                    if (key === 'age') return value !== null;
                    if (Array.isArray(value)) return value.length > 0;
                    return value && value !== '不限';
                  }).length} 项</li>
                  <li>打招呼数量：{maxContacts === '' ? 10 : maxContacts}</li>
                  {expectedPositions.length > 0 && (
                    <li>期望职位：{expectedPositions.join('、')}</li>
                  )}
                </ul>
              </div>
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => {
                  setSaveTemplateDialogOpen(false);
                  setTemplateName('');
                  setTemplateDescription('');
                }}
                disabled={savingTemplate}
              >
                取消
              </Button>
              <Button
                onClick={handleSaveTemplate}
                disabled={savingTemplate}
              >
                {savingTemplate ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    保存中...
                  </>
                ) : (
                  <>
                    <Save className="mr-2 h-4 w-4" />
                    保存模板
                  </>
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Zap className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold tracking-tight">自动化向导</h1>
            <p className="text-muted-foreground">
              快速配置并启动自动化招聘任务
            </p>
          </div>
        </div>
      </div>

      {/* 步骤指示器 */}
      <div className="flex items-center justify-center gap-3 py-6">
        <div className="flex items-center gap-2">
          <div
            className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
              currentStep === 'browser'
                ? 'bg-primary text-primary-foreground border-primary'
                : currentStep !== 'browser'
                ? 'bg-blue-50 text-blue-700 border-blue-700'
                : 'border-muted-foreground text-muted-foreground'
            }`}
          >
            {currentStep !== 'browser' ? <CheckCircle2 className="h-5 w-5" /> : '1'}
          </div>
          <span
            className={`font-medium text-sm ${
              currentStep === 'browser' ? 'text-primary' : 'text-muted-foreground'
            }`}
          >
            浏览器
          </span>
        </div>

        <div className="w-12 h-0.5 bg-muted" />

        <div className="flex items-center gap-2">
          <div
            className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
              currentStep === 'login'
                ? 'bg-primary text-primary-foreground border-primary'
                : isLoggedIn
                ? 'bg-blue-50 text-blue-700 border-blue-700'
                : 'border-muted-foreground text-muted-foreground'
            }`}
          >
            {isLoggedIn ? <CheckCircle2 className="h-5 w-5" /> : '2'}
          </div>
          <span
            className={`font-medium text-sm ${
              currentStep === 'login' ? 'text-primary' : 'text-muted-foreground'
            }`}
          >
            登录
          </span>
        </div>

        <div className="w-12 h-0.5 bg-muted" />

        <div className="flex items-center gap-2">
          <div
            className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
              currentStep === 'job-select'
                ? 'bg-primary text-primary-foreground border-primary'
                : selectedJobValue
                ? 'bg-blue-50 text-blue-700 border-blue-700'
                : 'border-muted-foreground text-muted-foreground'
            }`}
          >
            {selectedJobValue ? <CheckCircle2 className="h-5 w-5" /> : '3'}
          </div>
          <span
            className={`font-medium text-sm ${
              currentStep === 'job-select' ? 'text-primary' : 'text-muted-foreground'
            }`}
          >
            职位
          </span>
        </div>

        <div className="w-12 h-0.5 bg-muted" />

        <div className="flex items-center gap-2">
          <div
            className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
              currentStep === 'configure'
                ? 'bg-primary text-primary-foreground border-primary'
                : currentStep === 'confirm'
                ? 'bg-blue-50 text-blue-700 border-blue-700'
                : 'border-muted-foreground text-muted-foreground'
            }`}
          >
            {currentStep === 'confirm' ? <CheckCircle2 className="h-5 w-5" /> : '4'}
          </div>
          <span
            className={`font-medium text-sm ${
              currentStep === 'configure' ? 'text-primary' : 'text-muted-foreground'
            }`}
          >
            配置
          </span>
        </div>

        <div className="w-12 h-0.5 bg-muted" />

        <div className="flex items-center gap-2">
          <div
            className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
              currentStep === 'confirm'
                ? 'bg-primary text-primary-foreground border-primary'
                : 'border-muted-foreground text-muted-foreground'
            }`}
          >
            5
          </div>
          <span
            className={`font-medium text-sm ${
              currentStep === 'confirm' ? 'text-primary' : 'text-muted-foreground'
            }`}
          >
            启动
          </span>
        </div>
      </div>

      {/* 步骤内容 */}
      {currentStep === 'browser' && renderBrowserStep()}
      {currentStep === 'login' && renderLoginStep()}
      {currentStep === 'job-select' && renderJobSelectStep()}
      {currentStep === 'configure' && renderConfigureStep()}
      {currentStep === 'confirm' && renderConfirmStep()}
    </div>
  );
}
