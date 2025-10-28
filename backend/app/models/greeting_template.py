"""
打招呼消息模板数据模型
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class GreetingTemplateBase(SQLModel):
    """打招呼模板基础模型"""
    name: str = Field(description="模板名称")
    content: str = Field(description="模板内容，支持变量：{name}, {position}, {company}")
    is_active: bool = Field(default=True, description="是否启用")
    usage_count: int = Field(default=0, description="使用次数")


class GreetingTemplate(GreetingTemplateBase, table=True):
    """打招呼模板数据库模型"""
    __tablename__ = "greeting_templates"

    id: Optional[int] = Field(default=None, primary_key=True)

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")


class GreetingTemplateCreate(SQLModel):
    """创建打招呼模板的请求模型"""
    name: str
    content: str
    is_active: bool = True


class GreetingTemplateRead(GreetingTemplateBase):
    """读取打招呼模板的响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime


class GreetingTemplateUpdate(SQLModel):
    """更新打招呼模板的请求模型"""
    name: Optional[str] = None
    content: Optional[str] = None
    is_active: Optional[bool] = None
