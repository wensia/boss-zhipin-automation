"""
通知配置数据模型
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class NotificationConfig(SQLModel, table=True):
    """通知配置表"""
    __tablename__ = "notification_configs"

    id: Optional[int] = Field(default=None, primary_key=True)

    # 钉钉配置
    dingtalk_enabled: bool = Field(default=False, description="是否启用钉钉通知")
    dingtalk_webhook: Optional[str] = Field(default=None, description="钉钉机器人Webhook地址")
    dingtalk_secret: Optional[str] = Field(default=None, description="钉钉机器人签名密钥（可选）")

    # 飞书配置
    feishu_enabled: bool = Field(default=False, description="是否启用飞书通知")
    feishu_webhook: Optional[str] = Field(default=None, description="飞书机器人Webhook地址")
    feishu_secret: Optional[str] = Field(default=None, description="飞书机器人签名密钥（可选）")

    # 飞书多维表格配置
    feishu_bitable_enabled: bool = Field(default=False, description="是否启用飞书多维表格同步")
    feishu_app_id: Optional[str] = Field(default=None, description="飞书应用App ID")
    feishu_app_secret: Optional[str] = Field(default=None, description="飞书应用App Secret")
    feishu_app_token: Optional[str] = Field(default=None, description="飞书多维表格App Token")
    feishu_table_id: Optional[str] = Field(default=None, description="飞书数据表Table ID")

    # 通知设置
    notify_on_completion: bool = Field(default=True, description="任务完成时通知")
    notify_on_limit: bool = Field(default=True, description="触发限制时通知")
    notify_on_error: bool = Field(default=True, description="发生错误时通知")

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")


class NotificationConfigCreate(SQLModel):
    """创建通知配置的请求模型"""
    dingtalk_enabled: bool = False
    dingtalk_webhook: Optional[str] = None
    dingtalk_secret: Optional[str] = None
    feishu_enabled: bool = False
    feishu_webhook: Optional[str] = None
    feishu_secret: Optional[str] = None
    feishu_bitable_enabled: bool = False
    feishu_app_id: Optional[str] = None
    feishu_app_secret: Optional[str] = None
    feishu_app_token: Optional[str] = None
    feishu_table_id: Optional[str] = None
    notify_on_completion: bool = True
    notify_on_limit: bool = True
    notify_on_error: bool = True


class NotificationConfigUpdate(SQLModel):
    """更新通知配置的请求模型"""
    dingtalk_enabled: Optional[bool] = None
    dingtalk_webhook: Optional[str] = None
    dingtalk_secret: Optional[str] = None
    feishu_enabled: Optional[bool] = None
    feishu_webhook: Optional[str] = None
    feishu_secret: Optional[str] = None
    feishu_bitable_enabled: Optional[bool] = None
    feishu_app_id: Optional[str] = None
    feishu_app_secret: Optional[str] = None
    feishu_app_token: Optional[str] = None
    feishu_table_id: Optional[str] = None
    notify_on_completion: Optional[bool] = None
    notify_on_limit: Optional[bool] = None
    notify_on_error: Optional[bool] = None
