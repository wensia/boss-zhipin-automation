"""
示例数据模型
根据实际需求修改此文件
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class JobBase(SQLModel):
    """职位基础模型"""
    title: str = Field(description="职位名称")
    company: str = Field(description="公司名称")
    salary: str = Field(description="薪资范围")
    location: str = Field(description="工作地点")
    description: Optional[str] = Field(default=None, description="职位描述")


class Job(JobBase, table=True):
    """职位数据库模型"""
    __tablename__ = "jobs"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")


class JobCreate(JobBase):
    """创建职位的请求模型"""
    pass


class JobRead(JobBase):
    """读取职位的响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime


class JobUpdate(SQLModel):
    """更新职位的请求模型"""
    title: Optional[str] = None
    company: Optional[str] = None
    salary: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
