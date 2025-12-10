/**
 * 账号管理页面
 */
import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { useAccounts } from '@/hooks/useAccounts';
import { useCurrentAccount } from '@/hooks/useCurrentAccount';
import type { UserAccount } from '@/types/account';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { User, Building2, Mail, Calendar, CheckCircle2, Star, TrendingUp, TrendingDown, RefreshCw, Chrome } from 'lucide-react';
import axios from 'axios';

interface RecruitData {
  view: number;
  viewCTY: number;
  viewed: number;
  viewedCTY: number;
  chat: number;
  chatCTY: number;
  chatInitiative: number;
  chatInitiativeCTY: number;
  contactMe: number;
  contactMeCTY: number;
  resume: number;
  resumeCTY: number;
  exchangePhoneAndWeiXin: number;
  exchangePhoneAndWeiXinCTY: number;
  interview: number;
  interviewCTY: number;
  interviewAccept: number;
  interviewAcceptCTY: number;
  chatInitiativeRightsConsumption: number;
  viewRightsConsumption: number;
}

export default function Accounts() {
  const { getAccounts, deleteAccount, loading, error } = useAccounts();
  const { currentAccount, switchToAccount, switching } = useCurrentAccount();
  const [accounts, setAccounts] = useState<UserAccount[]>([]);
  const [recruitDataMap, setRecruitDataMap] = useState<Record<number, RecruitData>>({});
  const [refreshingMap, setRefreshingMap] = useState<Record<number, boolean>>({});
  const [openingBrowserMap, setOpeningBrowserMap] = useState<Record<number, boolean>>({});

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      const data = await getAccounts();
      setAccounts(data);
      // 加载每个账号的招聘数据
      data.forEach((account) => {
        loadRecruitData(account.id);
      });
    } catch (err) {
      console.error('加载账号列表失败:', err);
    }
  };

  const loadRecruitData = async (accountId: number, showToast: boolean = false) => {
    try {
      setRefreshingMap((prev) => ({ ...prev, [accountId]: true }));

      const API_BASE_URL = import.meta.env.VITE_API_URL || '';
      const response = await axios.get(`${API_BASE_URL}/api/accounts/${accountId}/recruit-data`);

      if (response.data?.zpData?.todayData) {
        setRecruitDataMap((prev) => ({
          ...prev,
          [accountId]: response.data.zpData.todayData,
        }));

        if (showToast) {
          toast.success('数据刷新成功');
        }
      }
    } catch (err) {
      // 忽略错误，某些账号可能未登录
      console.log(`账号${accountId}招聘数据加载失败:`, err);
      if (showToast) {
        toast.error('数据刷新失败，请确保账号已登录');
      }
    } finally {
      setRefreshingMap((prev) => ({ ...prev, [accountId]: false }));
    }
  };

  const handleRefreshRecruitData = async (accountId: number) => {
    await loadRecruitData(accountId, true);
  };

  const handleOpenBrowser = async (account: UserAccount) => {
    try {
      setOpeningBrowserMap((prev) => ({ ...prev, [account.id]: true }));
      toast.loading(`正在打开${account.show_name}的浏览器窗口...`, { id: `open-browser-${account.id}` });

      const API_BASE_URL = import.meta.env.VITE_API_URL || '';
      const response = await axios.post(`${API_BASE_URL}/api/automation/init`, null, {
        params: {
          headless: false,
          com_id: account.com_id
        }
      });

      if (response.data?.success) {
        toast.success(`已成功打开${account.show_name}的浏览器窗口`, { id: `open-browser-${account.id}` });
      } else {
        toast.error('打开浏览器失败', { id: `open-browser-${account.id}` });
      }
    } catch (err) {
      console.error('打开浏览器失败:', err);
      toast.error(err instanceof Error ? err.message : '打开浏览器失败', { id: `open-browser-${account.id}` });
    } finally {
      setOpeningBrowserMap((prev) => ({ ...prev, [account.id]: false }));
    }
  };

  const handleDelete = async (accountId: number) => {
    if (!confirm('确定要删除这个账号吗？')) {
      return;
    }

    try {
      await deleteAccount(accountId);
      await loadAccounts();
    } catch (err) {
      console.error('删除账号失败:', err);
      alert('删除账号失败');
    }
  };

  const handleSwitchAccount = async (accountId: number) => {
    try {
      toast.loading('正在切换账号...', { id: 'switch' });
      await switchToAccount(accountId);
      toast.success('账号切换成功', { id: 'switch' });
    } catch (error) {
      toast.error(error instanceof Error ? error.message : '切换失败', { id: 'switch' });
    }
  };

  const isCurrentAccount = (accountId: number) => {
    return currentAccount?.id === accountId;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">账号管理</h1>
        <p className="text-muted-foreground mt-2">
          管理已登录的Boss直聘账号
        </p>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {loading && accounts.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          加载中...
        </div>
      ) : accounts.length === 0 ? (
        <Card>
          <CardContent className="py-12">
            <div className="text-center text-muted-foreground">
              <User className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg mb-2">暂无账号</p>
              <p className="text-sm">
                在向导中扫码登录后，账号信息会自动保存到这里
              </p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {accounts.map((account) => (
            <Card key={account.id} className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <Avatar className="h-12 w-12">
                      <AvatarImage src={account.avatar} alt={account.show_name} />
                      <AvatarFallback>{account.show_name[0]}</AvatarFallback>
                    </Avatar>
                    <div>
                      <div className="flex items-center gap-2">
                        <CardTitle className="text-lg">{account.show_name}</CardTitle>
                        {isCurrentAccount(account.id) && (
                          <Badge className="bg-blue-600 text-white">
                            <Star className="h-3 w-3 mr-1 fill-white" />
                            当前账号
                          </Badge>
                        )}
                      </div>
                      <CardDescription className="text-xs">
                        {account.gender === 1 ? '男' : account.gender === 2 ? '女' : '未知'}
                      </CardDescription>
                    </div>
                  </div>
                  {account.cert && (
                    <Badge variant="outline" className="text-green-600 border-green-600">
                      <CheckCircle2 className="h-3 w-3 mr-1" />
                      已认证
                    </Badge>
                  )}
                </div>
              </CardHeader>

              <CardContent className="space-y-3">
                {/* 职位信息 */}
                <div className="flex items-start gap-2 text-sm">
                  <User className="h-4 w-4 text-muted-foreground shrink-0 mt-0.5" />
                  <div>
                    <div className="font-medium">{account.title}</div>
                    <div className="text-muted-foreground text-xs">职位</div>
                  </div>
                </div>

                {/* 公司信息 */}
                <div className="flex items-start gap-2 text-sm">
                  <Building2 className="h-4 w-4 text-muted-foreground shrink-0 mt-0.5" />
                  <div>
                    <div className="font-medium">{account.company_short_name}</div>
                    <div className="text-muted-foreground text-xs">{account.industry}</div>
                  </div>
                </div>

                {/* 邮箱 */}
                {account.resume_email && (
                  <div className="flex items-center gap-2 text-sm">
                    <Mail className="h-4 w-4 text-muted-foreground shrink-0" />
                    <div className="truncate text-muted-foreground">
                      {account.resume_email}
                    </div>
                  </div>
                )}

                {/* 上次登录 */}
                <div className="flex items-center gap-2 text-sm pt-2 border-t">
                  <Calendar className="h-4 w-4 text-muted-foreground shrink-0" />
                  <div className="text-muted-foreground text-xs">
                    上次登录: {formatDate(account.last_login_at)}
                  </div>
                </div>

                {/* 今日招聘数据 */}
                {recruitDataMap[account.id] && (
                  <div className="pt-3 border-t space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="text-sm font-semibold text-gray-700">今日招聘数据</div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRefreshRecruitData(account.id)}
                        disabled={refreshingMap[account.id]}
                        className="h-7 px-2"
                      >
                        <RefreshCw className={`h-3.5 w-3.5 ${refreshingMap[account.id] ? 'animate-spin' : ''}`} />
                        <span className="ml-1 text-xs">刷新</span>
                      </Button>
                    </div>

                    {/* 第一行：我看过、看过我、我打招呼 */}
                    <div className="grid grid-cols-3 gap-2">
                      <div className="bg-gradient-to-br from-cyan-50 to-cyan-100 rounded-lg p-3 border border-cyan-200">
                        <div className="text-xs text-gray-600 mb-1">我看过</div>
                        <div className="text-xl font-bold text-gray-900">{recruitDataMap[account.id].view}</div>
                        <div className="flex items-center gap-1 text-xs">
                          <span className="text-gray-600">较昨日</span>
                          <span className={recruitDataMap[account.id].viewCTY >= 0 ? 'text-green-600' : 'text-red-600'}>
                            {recruitDataMap[account.id].viewCTY > 0 ? `+${recruitDataMap[account.id].viewCTY}` : recruitDataMap[account.id].viewCTY}
                          </span>
                        </div>
                      </div>

                      <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-3 border border-blue-200">
                        <div className="text-xs text-gray-600 mb-1">看过我</div>
                        <div className="text-xl font-bold text-gray-900">{recruitDataMap[account.id].viewed}</div>
                        <div className="flex items-center gap-1 text-xs">
                          <span className="text-gray-600">较昨日</span>
                          <span className={recruitDataMap[account.id].viewedCTY >= 0 ? 'text-green-600' : 'text-red-600'}>
                            {recruitDataMap[account.id].viewedCTY > 0 ? `+${recruitDataMap[account.id].viewedCTY}` : recruitDataMap[account.id].viewedCTY}
                          </span>
                        </div>
                      </div>

                      <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-3 border border-purple-200">
                        <div className="text-xs text-gray-600 mb-1">我打招呼</div>
                        <div className="text-xl font-bold text-gray-900">{recruitDataMap[account.id].chatInitiative}</div>
                        <div className="flex items-center gap-1 text-xs">
                          <span className="text-gray-600">较昨日</span>
                          <span className={recruitDataMap[account.id].chatInitiativeCTY >= 0 ? 'text-green-600' : 'text-red-600'}>
                            {recruitDataMap[account.id].chatInitiativeCTY > 0 ? `+${recruitDataMap[account.id].chatInitiativeCTY}` : recruitDataMap[account.id].chatInitiativeCTY}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* 第二行：我沟通、收获简历、交换电话微信、接受面试 */}
                    <div className="grid grid-cols-4 gap-2">
                      <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-lg p-2 border border-indigo-200">
                        <div className="text-xs text-gray-600 mb-1">我沟通</div>
                        <div className="text-lg font-bold text-gray-900">{recruitDataMap[account.id].chat}</div>
                        <div className="text-xs text-gray-600">较昨 {recruitDataMap[account.id].chatCTY > 0 ? `+${recruitDataMap[account.id].chatCTY}` : recruitDataMap[account.id].chatCTY}</div>
                      </div>

                      <div className="bg-gradient-to-br from-pink-50 to-pink-100 rounded-lg p-2 border border-pink-200">
                        <div className="text-xs text-gray-600 mb-1">收获简历</div>
                        <div className="text-lg font-bold text-gray-900">{recruitDataMap[account.id].resume}</div>
                        <div className="text-xs text-gray-600">较昨 {recruitDataMap[account.id].resumeCTY > 0 ? `+${recruitDataMap[account.id].resumeCTY}` : recruitDataMap[account.id].resumeCTY}</div>
                      </div>

                      <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-2 border border-green-200">
                        <div className="text-xs text-gray-600 mb-1">交换联系</div>
                        <div className="text-lg font-bold text-gray-900">{recruitDataMap[account.id].exchangePhoneAndWeiXin}</div>
                        <div className="text-xs text-gray-600">较昨 {recruitDataMap[account.id].exchangePhoneAndWeiXinCTY > 0 ? `+${recruitDataMap[account.id].exchangePhoneAndWeiXinCTY}` : recruitDataMap[account.id].exchangePhoneAndWeiXinCTY}</div>
                      </div>

                      <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-lg p-2 border border-yellow-200">
                        <div className="text-xs text-gray-600 mb-1">接受面试</div>
                        <div className="text-lg font-bold text-gray-900">{recruitDataMap[account.id].interview}</div>
                        <div className="text-xs text-gray-600">较昨 {recruitDataMap[account.id].interviewCTY > 0 ? `+${recruitDataMap[account.id].interviewCTY}` : recruitDataMap[account.id].interviewCTY}</div>
                      </div>
                    </div>

                    {/* 权益消耗信息 */}
                    <div className="bg-orange-50 rounded-lg p-3 border border-orange-200">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-medium text-gray-700">今日权益使用</span>
                        <Badge variant="outline" className="text-orange-600 border-orange-300">
                          剩余 {200 - recruitDataMap[account.id].chatInitiativeRightsConsumption} 次
                        </Badge>
                      </div>
                      <div className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span className="text-gray-600">新打招呼次数（去重）</span>
                          <span className="font-semibold text-gray-900">{recruitDataMap[account.id].chatInitiativeRightsConsumption} 次</span>
                        </div>
                        <div className="flex justify-between text-xs">
                          <span className="text-gray-600">查看候选人</span>
                          <span className="font-semibold text-gray-900">{recruitDataMap[account.id].viewRightsConsumption} 次</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* 操作按钮 */}
                <div className="flex flex-col gap-2 pt-2">
                  <div className="flex gap-2">
                    {!isCurrentAccount(account.id) && (
                      <Button
                        variant="default"
                        size="sm"
                        className="flex-1"
                        onClick={() => handleSwitchAccount(account.id)}
                        disabled={switching}
                      >
                        <Star className="h-4 w-4 mr-1" />
                        设为当前账号
                      </Button>
                    )}
                    <Button
                      variant="outline"
                      size="sm"
                      className={isCurrentAccount(account.id) ? 'flex-1' : ''}
                      onClick={() => {
                        try {
                          const rawData = JSON.parse(account.raw_data);
                          console.log('账号详情:', rawData);
                          alert('查看控制台查看完整信息');
                        } catch (err) {
                          alert('无法解析原始数据');
                        }
                      }}
                    >
                      查看详情
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDelete(account.id)}
                      disabled={isCurrentAccount(account.id)}
                    >
                      删除
                    </Button>
                  </div>

                  {/* 打开浏览器按钮 */}
                  <Button
                    variant="secondary"
                    size="sm"
                    className="w-full"
                    onClick={() => handleOpenBrowser(account)}
                    disabled={openingBrowserMap[account.id]}
                  >
                    <Chrome className={`h-4 w-4 mr-1 ${openingBrowserMap[account.id] ? 'animate-pulse' : ''}`} />
                    {openingBrowserMap[account.id] ? '正在打开浏览器...' : '打开浏览器窗口'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* 统计信息 */}
      {accounts.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">统计信息</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold">{accounts.length}</div>
                <div className="text-sm text-muted-foreground">总账号数</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">
                  {accounts.filter((a) => a.cert).length}
                </div>
                <div className="text-sm text-muted-foreground">已认证</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-yellow-600">
                  {accounts.filter((a) => a.is_gold > 0).length}
                </div>
                <div className="text-sm text-muted-foreground">金牌猎头</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
