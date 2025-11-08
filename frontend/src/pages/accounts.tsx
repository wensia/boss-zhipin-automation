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
import { User, Building2, Mail, Calendar, CheckCircle2, Star } from 'lucide-react';

export default function Accounts() {
  const { getAccounts, deleteAccount, loading, error } = useAccounts();
  const { currentAccount, switchToAccount, switching } = useCurrentAccount();
  const [accounts, setAccounts] = useState<UserAccount[]>([]);

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      const data = await getAccounts();
      setAccounts(data);
    } catch (err) {
      console.error('加载账号列表失败:', err);
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
