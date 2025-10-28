"""
自动化任务数据模型
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"        # 待执行
    RUNNING = "running"        # 执行中
    PAUSED = "paused"          # 已暂停
    COMPLETED = "completed"    # 已完成
    FAILED = "failed"          # 失败
    CANCELLED = "cancelled"    # 已取消


class AutomationTaskBase(SQLModel):
    """自动化任务基础模型"""
    # 任务配置
    name: str = Field(description="任务名称")
    search_keywords: str = Field(description="搜索关键词")
    filters: Optional[str] = Field(default=None, description="筛选条件（JSON字符串）")
    greeting_template_id: int = Field(foreign_key="greeting_templates.id", description="打招呼模板ID")

    # 执行配置
    max_contacts: int = Field(default=50, description="最大沟通数量")
    delay_min: int = Field(default=2, description="最小延迟（秒）")
    delay_max: int = Field(default=5, description="最大延迟（秒）")

    # 任务状态
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="任务状态")
    progress: int = Field(default=0, description="进度（0-100）")

    # 执行结果
    total_found: int = Field(default=0, description="找到的求职者总数")
    total_contacted: int = Field(default=0, description="已沟通数量")
    total_success: int = Field(default=0, description="成功数量")
    total_failed: int = Field(default=0, description="失败数量")

    error_message: Optional[str] = Field(default=None, description="错误信息")


class AutomationTask(AutomationTaskBase, table=True):
    """自动化任务数据库模型"""
    __tablename__ = "automation_tasks"

    id: Optional[int] = Field(default=None, primary_key=True)

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    started_at: Optional[datetime] = Field(default=None, description="开始时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")


class AutomationTaskCreate(SQLModel):
    """创建自动化任务的请求模型"""
    name: str
    search_keywords: str
    filters: Optional[str] = None
    greeting_template_id: int
    max_contacts: int = 50
    delay_min: int = 2
    delay_max: int = 5


class AutomationTaskRead(AutomationTaskBase):
    """读取自动化任务的响应模型"""
    id: int
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


class AutomationTaskUpdate(SQLModel):
    """更新自动化任务的请求模型"""
    name: Optional[str] = None
    status: Optional[TaskStatus] = None
    progress: Optional[int] = None
    total_found: Optional[int] = None
    total_contacted: Optional[int] = None
    total_success: Optional[int] = None
    total_failed: Optional[int] = None
    error_message: Optional[str] = None
