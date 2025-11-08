/**
 * 通知配置相关类型定义
 */

export interface NotificationConfig {
  id: number;
  // 钉钉配置
  dingtalk_enabled: boolean;
  dingtalk_webhook: string | null;
  dingtalk_secret: string | null;
  // 飞书配置
  feishu_enabled: boolean;
  feishu_webhook: string | null;
  feishu_secret: string | null;
  // 飞书多维表格配置
  feishu_bitable_enabled: boolean;
  feishu_app_id: string | null;
  feishu_app_secret: string | null;
  feishu_app_token: string | null;
  feishu_table_id: string | null;
  // 通知设置
  notify_on_completion: boolean;
  notify_on_limit: boolean;
  notify_on_error: boolean;
  created_at: string;
  updated_at: string;
}

export interface NotificationConfigUpdate {
  // 钉钉配置
  dingtalk_enabled?: boolean;
  dingtalk_webhook?: string | null;
  dingtalk_secret?: string | null;
  // 飞书配置
  feishu_enabled?: boolean;
  feishu_webhook?: string | null;
  feishu_secret?: string | null;
  // 飞书多维表格配置
  feishu_bitable_enabled?: boolean;
  feishu_app_id?: string | null;
  feishu_app_secret?: string | null;
  feishu_app_token?: string | null;
  feishu_table_id?: string | null;
  // 通知设置
  notify_on_completion?: boolean;
  notify_on_limit?: boolean;
  notify_on_error?: boolean;
}
