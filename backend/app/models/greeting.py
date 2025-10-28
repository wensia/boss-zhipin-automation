"""
打招呼记录数据模型
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class GreetingRecordBase(SQLModel):
    """打招呼记录基础模型"""
    # 关联信息
    candidate_id: int = Field(foreign_key="candidates.id", description="求职者ID")
    task_id: Optional[int] = Field(default=None, foreign_key="automation_tasks.id", description="任务ID")

    # 消息内容
    message: str = Field(description="打招呼消息内容")
    template_id: Optional[int] = Field(default=None, foreign_key="greeting_templates.id", description="使用的模板ID")

    # 执行结果
    success: bool = Field(default=True, description="是否成功")
    error_message: Optional[str] = Field(default=None, description="错误信息")


class GreetingRecord(GreetingRecordBase, table=True):
    """打招呼记录数据库模型"""
    __tablename__ = "greeting_records"

    id: Optional[int] = Field(default=None, primary_key=True)

    # 时间戳
    sent_at: datetime = Field(default_factory=datetime.now, description="发送时间")


class GreetingRecordCreate(GreetingRecordBase):
    """创建打招呼记录的请求模型"""
    pass


class GreetingRecordRead(GreetingRecordBase):
    """读取打招呼记录的响应模型"""
    id: int
    sent_at: datetime
