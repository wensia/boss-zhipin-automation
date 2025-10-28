"""
系统配置数据模型
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, date


class SystemConfigBase(SQLModel):
    """系统配置基础模型"""
    # Boss 直聘账号配置
    boss_username: Optional[str] = Field(default=None, description="Boss账号")
    boss_session_saved: bool = Field(default=False, description="是否已保存登录状态")

    # 自动化配置
    auto_mode_enabled: bool = Field(default=False, description="是否启用自动模式")
    daily_limit: int = Field(default=100, description="每日沟通上限")
    today_contacted: int = Field(default=0, description="今日已沟通数")
    last_reset_date: Optional[date] = Field(default=None, description="上次重置日期")

    # 反爬虫配置
    anti_detection_enabled: bool = Field(default=True, description="是否启用反检测")
    random_delay_enabled: bool = Field(default=True, description="是否启用随机延迟")
    rest_interval: int = Field(default=15, description="休息间隔（处理多少个后休息）")
    rest_duration: int = Field(default=60, description="休息时长（秒）")


class SystemConfig(SystemConfigBase, table=True):
    """系统配置数据库模型"""
    __tablename__ = "system_config"

    id: Optional[int] = Field(default=None, primary_key=True)

    # 时间戳
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")


class SystemConfigRead(SystemConfigBase):
    """读取系统配置的响应模型"""
    id: int
    updated_at: datetime


class SystemConfigUpdate(SQLModel):
    """更新系统配置的请求模型"""
    boss_username: Optional[str] = None
    boss_session_saved: Optional[bool] = None
    auto_mode_enabled: Optional[bool] = None
    daily_limit: Optional[int] = None
    today_contacted: Optional[int] = None
    last_reset_date: Optional[date] = None
    anti_detection_enabled: Optional[bool] = None
    random_delay_enabled: Optional[bool] = None
    rest_interval: Optional[int] = None
    rest_duration: Optional[int] = None
