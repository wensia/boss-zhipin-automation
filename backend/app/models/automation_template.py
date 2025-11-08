"""
自动化模板数据模型
用于保存和复用整个自动化流程的配置
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Column, JSON


class AutomationTemplateBase(SQLModel):
    """自动化模板基础模型"""
    name: str = Field(description="模板名称")
    description: Optional[str] = Field(default=None, description="模板描述")

    # 关联账号
    account_id: Optional[int] = Field(
        default=None,
        foreign_key="user_accounts.id",
        description="关联的账号ID"
    )

    # 浏览器配置
    headless: bool = Field(default=False, description="是否无头模式")

    # 职位配置
    job_id: Optional[str] = Field(default=None, description="职位ID")
    job_name: Optional[str] = Field(default=None, description="职位名称")

    # 筛选条件（JSON格式存储FilterOptions）
    filters: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON),
        description="筛选条件配置"
    )

    # 打招呼配置
    greeting_count: int = Field(
        default=50,
        ge=1,
        le=300,
        description="打招呼数量"
    )
    expected_positions: Optional[list] = Field(
        default=None,
        sa_column=Column(JSON),
        description="期望职位关键词列表"
    )

    # 使用统计
    usage_count: int = Field(default=0, description="使用次数")


class AutomationTemplate(AutomationTemplateBase, table=True):
    """自动化模板表"""
    __tablename__ = "automation_templates"

    id: Optional[int] = Field(default=None, primary_key=True)

    # 时间戳
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="更新时间"
    )
    last_used_at: Optional[datetime] = Field(
        default=None,
        description="最后使用时间"
    )


class AutomationTemplateCreate(AutomationTemplateBase):
    """创建自动化模板"""
    pass


class AutomationTemplateUpdate(SQLModel):
    """更新自动化模板"""
    name: Optional[str] = None
    description: Optional[str] = None
    account_id: Optional[int] = None
    headless: Optional[bool] = None
    job_id: Optional[str] = None
    job_name: Optional[str] = None
    filters: Optional[dict] = None
    greeting_count: Optional[int] = None
    expected_positions: Optional[list] = None


class AutomationTemplateRead(AutomationTemplateBase):
    """读取自动化模板"""
    id: int
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime]
