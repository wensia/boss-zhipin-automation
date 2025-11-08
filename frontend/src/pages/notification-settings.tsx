/**
 * 通知设置页面
 */
import { useEffect, useState } from 'react';
import { Bell, TestTube, Save, Loader2, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';

import { useNotification } from '@/hooks/useNotification';
import type { NotificationConfig } from '@/types/notification';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';

export default function NotificationSettings() {
  const { getConfig, updateConfig, testDingtalk, testFeishu, testFeishuBitable, syncGreetingFields, loading } = useNotification();

  const [config, setConfig] = useState<NotificationConfig | null>(null);
  const [isTesting, setIsTesting] = useState(false);
  const [isTestingFeishu, setIsTestingFeishu] = useState(false);
  const [isTestingBitable, setIsTestingBitable] = useState(false);
  const [isSyncingFields, setIsSyncingFields] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // 钉钉表单状态
  const [dingtalkEnabled, setDingtalkEnabled] = useState(false);
  const [dingtalkWebhook, setDingtalkWebhook] = useState('');
  const [dingtalkSecret, setDingtalkSecret] = useState('');

  // 飞书表单状态
  const [feishuEnabled, setFeishuEnabled] = useState(false);
  const [feishuWebhook, setFeishuWebhook] = useState('');
  const [feishuSecret, setFeishuSecret] = useState('');

  // 飞书多维表格表单状态
  const [feishuBitableEnabled, setFeishuBitableEnabled] = useState(false);
  const [feishuAppId, setFeishuAppId] = useState('');
  const [feishuAppSecret, setFeishuAppSecret] = useState('');
  const [feishuAppToken, setFeishuAppToken] = useState('');
  const [feishuTableId, setFeishuTableId] = useState('');
  const [feishuTableUrl, setFeishuTableUrl] = useState('');

  // 通知设置
  const [notifyOnCompletion, setNotifyOnCompletion] = useState(true);
  const [notifyOnLimit, setNotifyOnLimit] = useState(true);
  const [notifyOnError, setNotifyOnError] = useState(true);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const data = await getConfig();
      setConfig(data);

      // 更新钉钉表单状态
      setDingtalkEnabled(data.dingtalk_enabled);
      setDingtalkWebhook(data.dingtalk_webhook || '');
      setDingtalkSecret(data.dingtalk_secret || '');

      // 更新飞书表单状态
      setFeishuEnabled(data.feishu_enabled);
      setFeishuWebhook(data.feishu_webhook || '');
      setFeishuSecret(data.feishu_secret || '');

      // 更新飞书多维表格状态
      setFeishuBitableEnabled(data.feishu_bitable_enabled);
      setFeishuAppId(data.feishu_app_id || '');
      setFeishuAppSecret(data.feishu_app_secret || '');
      setFeishuAppToken(data.feishu_app_token || '');
      setFeishuTableId(data.feishu_table_id || '');

      // 更新通知设置
      setNotifyOnCompletion(data.notify_on_completion);
      setNotifyOnLimit(data.notify_on_limit);
      setNotifyOnError(data.notify_on_error);
    } catch (error) {
      toast.error('加载配置失败');
      console.error('Failed to load config:', error);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await updateConfig({
        dingtalk_enabled: dingtalkEnabled,
        dingtalk_webhook: dingtalkWebhook || null,
        dingtalk_secret: dingtalkSecret || null,
        feishu_enabled: feishuEnabled,
        feishu_webhook: feishuWebhook || null,
        feishu_secret: feishuSecret || null,
        feishu_bitable_enabled: feishuBitableEnabled,
        feishu_app_id: feishuAppId || null,
        feishu_app_secret: feishuAppSecret || null,
        feishu_app_token: feishuAppToken || null,
        feishu_table_id: feishuTableId || null,
        notify_on_completion: notifyOnCompletion,
        notify_on_limit: notifyOnLimit,
        notify_on_error: notifyOnError,
      });
      toast.success('配置已保存');
      await loadConfig();
    } catch (error) {
      toast.error('保存失败');
      console.error('Failed to save config:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleTest = async () => {
    if (!dingtalkEnabled) {
      toast.error('请先启用钉钉通知');
      return;
    }

    if (!dingtalkWebhook) {
      toast.error('请先配置 Webhook 地址');
      return;
    }

    setIsTesting(true);
    try {
      // 先保存配置
      await handleSave();

      const result = await testDingtalk();
      if (result.success) {
        toast.success('测试消息已发送，请查收！');
      } else {
        toast.error('测试失败');
      }
    } catch (error: any) {
      toast.error(error.message || '测试失败');
      console.error('Failed to test dingtalk:', error);
    } finally {
      setIsTesting(false);
    }
  };

  const handleTestFeishu = async () => {
    if (!feishuEnabled) {
      toast.error('请先启用飞书通知');
      return;
    }

    if (!feishuWebhook) {
      toast.error('请先配置飞书 Webhook 地址');
      return;
    }

    setIsTestingFeishu(true);
    try {
      // 先保存配置
      await handleSave();

      const result = await testFeishu();
      if (result.success) {
        toast.success('飞书测试消息已发送，请查收！');
      } else {
        toast.error('测试失败');
      }
    } catch (error: any) {
      toast.error(error.message || '测试失败');
      console.error('Failed to test feishu:', error);
    } finally {
      setIsTestingFeishu(false);
    }
  };

  const parseFeishuTableUrl = (url: string) => {
    try {
      // 移除首尾空格
      url = url.trim();

      // 匹配格式: https://xxx.feishu.cn/base/APP_TOKEN?table=TABLE_ID
      // 或: https://xxx.feishu.cn/sheets/APP_TOKEN?table=TABLE_ID
      const patterns = [
        /\/base\/([^?]+)\?.*table=([^&]+)/,
        /\/sheets\/([^?]+)\?.*table=([^&]+)/,
        /\/base\/([^?]+)$/,  // 只有 app token
      ];

      for (const pattern of patterns) {
        const match = url.match(pattern);
        if (match) {
          const appToken = match[1];
          const tableId = match[2] || '';

          setFeishuAppToken(appToken);
          if (tableId) {
            setFeishuTableId(tableId);
            toast.success('已自动解析 App Token 和 Table ID');
          } else {
            toast.success('已自动解析 App Token');
            toast.info('请手动输入 Table ID');
          }
          return;
        }
      }

      toast.error('无法解析 URL，请检查格式');
    } catch (error) {
      console.error('Failed to parse URL:', error);
      toast.error('URL 解析失败');
    }
  };

  const handleFeishuTableUrlChange = (url: string) => {
    setFeishuTableUrl(url);
    if (url.includes('feishu.cn')) {
      parseFeishuTableUrl(url);
    }
  };

  const handleTestBitable = async () => {
    if (!feishuBitableEnabled) {
      toast.error('请先启用飞书多维表格同步');
      return;
    }

    if (!feishuAppId || !feishuAppSecret) {
      toast.error('请先配置飞书应用凭证');
      return;
    }

    if (!feishuAppToken || !feishuTableId) {
      toast.error('请先配置飞书多维表格信息');
      return;
    }

    setIsTestingBitable(true);
    try {
      // 先保存配置
      await handleSave();

      const result = await testFeishuBitable();
      if (result.success) {
        toast.success(`连接成功！发现 ${result.field_count || 0} 个字段`);
      } else {
        toast.error('连接测试失败');
      }
    } catch (error: any) {
      toast.error(error.message || '连接测试失败');
      console.error('Failed to test feishu bitable:', error);
    } finally {
      setIsTestingBitable(false);
    }
  };

  const handleSyncGreetingFields = async () => {
    if (!feishuBitableEnabled) {
      toast.error('请先启用飞书多维表格同步');
      return;
    }

    if (!feishuAppId || !feishuAppSecret) {
      toast.error('请先配置飞书应用凭证');
      return;
    }

    if (!feishuAppToken || !feishuTableId) {
      toast.error('请先配置飞书多维表格信息');
      return;
    }

    setIsSyncingFields(true);
    try {
      // 先保存配置
      await handleSave();

      const result = await syncGreetingFields();
      if (result.success) {
        const message = `字段同步完成！已存在: ${result.existing_count} 个，新创建: ${result.created_count} 个${
          result.failed_count > 0 ? `，失败: ${result.failed_count} 个` : ''
        }`;
        toast.success(message);
      } else {
        toast.error('字段同步失败');
      }
    } catch (error: any) {
      toast.error(error.message || '字段同步失败');
      console.error('Failed to sync greeting fields:', error);
    } finally {
      setIsSyncingFields(false);
    }
  };

  if (loading && !config) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Bell className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold tracking-tight">通知设置</h1>
            <p className="text-muted-foreground">
              配置钉钉机器人通知，及时了解任务执行情况
            </p>
          </div>
        </div>
      </div>

      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          <strong>提示：</strong>
          钉钉/飞书机器人配置需要在群内创建自定义机器人，获取 Webhook 地址。
          <a
            href="https://open.dingtalk.com/document/robots/custom-robot-access"
            target="_blank"
            rel="noopener noreferrer"
            className="ml-2 text-primary hover:underline"
          >
            钉钉机器人教程
          </a>
          <span className="mx-2">|</span>
          <a
            href="https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot"
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary hover:underline"
          >
            飞书机器人教程
          </a>
        </AlertDescription>
      </Alert>

      <Card>
        <CardHeader>
          <CardTitle>钉钉机器人配置</CardTitle>
          <CardDescription>
            配置钉钉群机器人以接收任务通知
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>启用钉钉通知</Label>
              <p className="text-sm text-muted-foreground">
                开启后将通过钉钉机器人发送通知消息
              </p>
            </div>
            <Switch
              checked={dingtalkEnabled}
              onCheckedChange={setDingtalkEnabled}
            />
          </div>

          <Separator />

          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="webhook">Webhook 地址 *</Label>
              <Input
                id="webhook"
                type="url"
                placeholder="https://oapi.dingtalk.com/robot/send?access_token=..."
                value={dingtalkWebhook}
                onChange={(e) => setDingtalkWebhook(e.target.value)}
                disabled={!dingtalkEnabled}
              />
              <p className="text-sm text-muted-foreground">
                在钉钉群中创建自定义机器人后获取的 Webhook 地址
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="secret">签名密钥（可选）</Label>
              <Input
                id="secret"
                type="password"
                placeholder="SEC..."
                value={dingtalkSecret}
                onChange={(e) => setDingtalkSecret(e.target.value)}
                disabled={!dingtalkEnabled}
              />
              <p className="text-sm text-muted-foreground">
                如果钉钉机器人启用了加签验证，请填写签名密钥
              </p>
            </div>
          </div>

          <Separator />

          <div className="flex gap-3">
            <Button
              onClick={handleTest}
              disabled={isTesting || !dingtalkEnabled || !dingtalkWebhook}
              variant="outline"
              className="flex-1"
            >
              {isTesting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  测试中...
                </>
              ) : (
                <>
                  <TestTube className="mr-2 h-4 w-4" />
                  发送测试消息
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 飞书机器人配置 */}
      <Card>
        <CardHeader>
          <CardTitle>飞书机器人配置</CardTitle>
          <CardDescription>
            配置飞书群机器人以接收任务通知
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>启用飞书通知</Label>
              <p className="text-sm text-muted-foreground">
                开启后将通过飞书机器人发送通知消息
              </p>
            </div>
            <Switch
              checked={feishuEnabled}
              onCheckedChange={setFeishuEnabled}
            />
          </div>

          <Separator />

          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="feishu-webhook">Webhook 地址 *</Label>
              <Input
                id="feishu-webhook"
                type="url"
                placeholder="https://open.feishu.cn/open-apis/bot/v2/hook/..."
                value={feishuWebhook}
                onChange={(e) => setFeishuWebhook(e.target.value)}
                disabled={!feishuEnabled}
              />
              <p className="text-sm text-muted-foreground">
                在飞书群中创建自定义机器人后获取的 Webhook 地址
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="feishu-secret">签名密钥（可选）</Label>
              <Input
                id="feishu-secret"
                type="password"
                placeholder="签名密钥..."
                value={feishuSecret}
                onChange={(e) => setFeishuSecret(e.target.value)}
                disabled={!feishuEnabled}
              />
              <p className="text-sm text-muted-foreground">
                如果飞书机器人启用了签名验证，请填写签名密钥
              </p>
            </div>
          </div>

          <Separator />

          <div className="flex gap-3">
            <Button
              onClick={handleTestFeishu}
              disabled={isTestingFeishu || !feishuEnabled || !feishuWebhook}
              variant="outline"
              className="flex-1"
            >
              {isTestingFeishu ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  测试中...
                </>
              ) : (
                <>
                  <TestTube className="mr-2 h-4 w-4" />
                  发送测试消息
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 飞书多维表格配置 */}
      <Card>
        <CardHeader>
          <CardTitle>飞书多维表格配置</CardTitle>
          <CardDescription>
            配置飞书多维表格以同步候选人数据
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>启用多维表格同步</Label>
              <p className="text-sm text-muted-foreground">
                开启后将自动同步候选人数据到飞书多维表格
              </p>
            </div>
            <Switch
              checked={feishuBitableEnabled}
              onCheckedChange={setFeishuBitableEnabled}
            />
          </div>

          <Separator />

          <div className="space-y-4">
            {/* URL 自动解析 */}
            <div className="space-y-2">
              <Label htmlFor="feishu-table-url">表格 URL（可选）</Label>
              <Input
                id="feishu-table-url"
                type="url"
                placeholder="https://example.feishu.cn/base/xxx?table=xxx 或 https://example.feishu.cn/sheets/xxx?table=xxx"
                value={feishuTableUrl}
                onChange={(e) => handleFeishuTableUrlChange(e.target.value)}
                disabled={!feishuBitableEnabled}
              />
              <p className="text-sm text-muted-foreground">
                粘贴飞书表格完整 URL，系统将自动解析 App Token 和 Table ID
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="feishu-app-id">App ID *</Label>
                <Input
                  id="feishu-app-id"
                  placeholder="cli_xxx"
                  value={feishuAppId}
                  onChange={(e) => setFeishuAppId(e.target.value)}
                  disabled={!feishuBitableEnabled}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="feishu-app-secret">App Secret *</Label>
                <Input
                  id="feishu-app-secret"
                  type="password"
                  placeholder="应用密钥"
                  value={feishuAppSecret}
                  onChange={(e) => setFeishuAppSecret(e.target.value)}
                  disabled={!feishuBitableEnabled}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="feishu-app-token">App Token *</Label>
                <Input
                  id="feishu-app-token"
                  placeholder="多维表格ID"
                  value={feishuAppToken}
                  onChange={(e) => setFeishuAppToken(e.target.value)}
                  disabled={!feishuBitableEnabled}
                />
                <p className="text-sm text-muted-foreground">
                  多维表格的唯一标识
                </p>
              </div>
              <div className="space-y-2">
                <Label htmlFor="feishu-table-id">Table ID *</Label>
                <Input
                  id="feishu-table-id"
                  placeholder="数据表ID"
                  value={feishuTableId}
                  onChange={(e) => setFeishuTableId(e.target.value)}
                  disabled={!feishuBitableEnabled}
                />
                <p className="text-sm text-muted-foreground">
                  数据表的唯一标识
                </p>
              </div>
            </div>
          </div>

          <Separator />

          <div className="flex gap-3">
            <Button
              onClick={handleTestBitable}
              disabled={
                isTestingBitable ||
                isSyncingFields ||
                !feishuBitableEnabled ||
                !feishuAppId ||
                !feishuAppSecret ||
                !feishuAppToken ||
                !feishuTableId
              }
              variant="outline"
              className="flex-1"
            >
              {isTestingBitable ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  连接测试中...
                </>
              ) : (
                <>
                  <TestTube className="mr-2 h-4 w-4" />
                  测试连接
                </>
              )}
            </Button>
            <Button
              onClick={handleSyncGreetingFields}
              disabled={
                isSyncingFields ||
                isTestingBitable ||
                !feishuBitableEnabled ||
                !feishuAppId ||
                !feishuAppSecret ||
                !feishuAppToken ||
                !feishuTableId
              }
              variant="default"
              className="flex-1"
            >
              {isSyncingFields ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  同步中...
                </>
              ) : (
                <>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  同步打招呼字段
                </>
              )}
            </Button>
          </div>
          <p className="text-sm text-muted-foreground">
            💡 首次使用或更新系统后，点击"同步打招呼字段"按钮自动创建所需的表格字段结构
          </p>
        </CardContent>
      </Card>

      {/* 通知触发条件 */}
      <Card>
        <CardHeader>
          <CardTitle>通知触发条件</CardTitle>
          <CardDescription>
            配置何时发送通知（适用于所有已启用的通知方式）
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>任务完成时通知</Label>
              <p className="text-sm text-muted-foreground">
                打招呼任务正常完成时发送通知
              </p>
            </div>
            <Switch
              checked={notifyOnCompletion}
              onCheckedChange={setNotifyOnCompletion}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>触发限制时通知</Label>
              <p className="text-sm text-muted-foreground">
                检测到打招呼达到上限时发送通知
              </p>
            </div>
            <Switch
              checked={notifyOnLimit}
              onCheckedChange={setNotifyOnLimit}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>发生错误时通知</Label>
              <p className="text-sm text-muted-foreground">
                任务执行过程中发生错误时发送通知
              </p>
            </div>
            <Switch
              checked={notifyOnError}
              onCheckedChange={setNotifyOnError}
            />
          </div>

          <Separator />

          <Button
            onClick={handleSave}
            disabled={isSaving || loading}
            className="w-full"
          >
            {isSaving ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                保存中...
              </>
            ) : (
              <>
                <Save className="mr-2 h-4 w-4" />
                保存所有配置
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>消息预览</CardTitle>
          <CardDescription>
            以下是钉钉通知消息的示例
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <h4 className="text-sm font-medium flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-600" />
              任务完成通知
            </h4>
            <div className="rounded-lg bg-muted p-4 text-sm space-y-2">
              <p className="font-medium">🎉 打招呼任务完成</p>
              <p>**任务已完成**</p>
              <p>- ✅ 成功：63 个</p>
              <p>- ❌ 失败：0 个</p>
              <p>- ⏭️ 跳过：37 个</p>
              <p>- 📊 共处理：100 个候选人</p>
              <p>- ⏱️ 耗时：703.4 秒</p>
            </div>
          </div>

          <div className="space-y-2">
            <h4 className="text-sm font-medium flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-orange-600" />
              触发限制通知
            </h4>
            <div className="rounded-lg bg-muted p-4 text-sm space-y-2">
              <p className="font-medium">⚠️ 打招呼已达上限</p>
              <p>**检测到打招呼限制弹窗，任务已停止**</p>
              <p>- ✅ 成功：50 个</p>
              <p>- ❌ 失败：0 个</p>
              <p>- ⏭️ 跳过：20 个</p>
              <p>- 📊 共处理：70 个候选人</p>
              <p>**建议：** 请稍后再试，或明天继续</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
