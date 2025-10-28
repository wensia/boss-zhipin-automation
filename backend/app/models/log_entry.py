"""
运行日志数据模型
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class LogLevel(str, Enum):
    """日志级别枚举"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogAction(str, Enum):
    """日志操作类型枚举"""
    # 任务相关
    TASK_CREATE = "task_create"
    TASK_START = "task_start"
    TASK_PAUSE = "task_pause"
    TASK_RESUME = "task_resume"
    TASK_COMPLETE = "task_complete"
    TASK_FAIL = "task_fail"
    TASK_CANCEL = "task_cancel"

    # 登录相关
    LOGIN_INIT = "login_init"
    LOGIN_QRCODE_GET = "login_qrcode_get"
    LOGIN_QRCODE_REFRESH = "login_qrcode_refresh"
    LOGIN_CHECK = "login_check"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAIL = "login_fail"

    # 候选人相关
    CANDIDATE_SEARCH = "candidate_search"
    CANDIDATE_CONTACT = "candidate_contact"
    CANDIDATE_CONTACT_SUCCESS = "candidate_contact_success"
    CANDIDATE_CONTACT_FAIL = "candidate_contact_fail"

    # 系统相关
    SYSTEM_INIT = "system_init"
    SYSTEM_CLEANUP = "system_cleanup"
    SYSTEM_ERROR = "system_error"


class LogEntryBase(SQLModel):
    """运行日志基础模型"""
    level: LogLevel = Field(default=LogLevel.INFO, description="日志级别")
    action: LogAction = Field(description="操作类型")
    message: str = Field(description="日志消息")
    details: Optional[str] = Field(default=None, description="详细信息（JSON字符串）")

    # 关联任务（可选）
    task_id: Optional[int] = Field(default=None, foreign_key="automation_tasks.id", description="关联的任务ID")
    task_name: Optional[str] = Field(default=None, description="任务名称")

    # 用户信息（可选）
    user_id: Optional[str] = Field(default=None, description="用户ID")
    user_name: Optional[str] = Field(default=None, description="用户名")


class LogEntry(LogEntryBase, table=True):
    """运行日志数据库模型"""
    __tablename__ = "log_entries"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class LogEntryCreate(SQLModel):
    """创建日志条目的请求模型"""
    level: LogLevel = LogLevel.INFO
    action: LogAction
    message: str
    details: Optional[str] = None
    task_id: Optional[int] = None
    task_name: Optional[str] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None


class LogEntryRead(LogEntryBase):
    """读取日志条目的响应模型"""
    id: int
    created_at: datetime
