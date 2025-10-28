"""
求职者数据模型
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class CandidateStatus(str, Enum):
    """求职者状态枚举"""
    NEW = "new"                    # 新发现
    CONTACTED = "contacted"        # 已沟通
    REPLIED = "replied"            # 已回复
    INTERESTED = "interested"      # 有意向
    REJECTED = "rejected"          # 已拒绝
    ARCHIVED = "archived"          # 已归档


class CandidateBase(SQLModel):
    """求职者基础模型"""
    # Boss直聘用户ID（唯一标识）
    boss_id: str = Field(index=True, unique=True, description="Boss直聘用户ID")

    # 基本信息
    name: str = Field(description="姓名")
    avatar: Optional[str] = Field(default=None, description="头像URL")

    # 职业信息
    position: str = Field(description="当前职位")
    company: Optional[str] = Field(default=None, description="当前公司")
    work_experience: Optional[str] = Field(default=None, description="工作年限")
    education: Optional[str] = Field(default=None, description="学历")

    # 期望信息
    expected_position: Optional[str] = Field(default=None, description="期望职位")
    expected_salary: Optional[str] = Field(default=None, description="期望薪资")
    expected_location: Optional[str] = Field(default=None, description="期望地点")

    # 状态信息
    status: CandidateStatus = Field(default=CandidateStatus.NEW, description="状态")
    active_time: Optional[datetime] = Field(default=None, description="最近活跃时间")
    last_contacted_at: Optional[datetime] = Field(default=None, description="最后沟通时间")

    # 其他信息
    profile_url: Optional[str] = Field(default=None, description="个人主页URL")
    tags: Optional[str] = Field(default=None, description="标签（JSON字符串）")
    notes: Optional[str] = Field(default=None, description="备注")


class Candidate(CandidateBase, table=True):
    """求职者数据库模型"""
    __tablename__ = "candidates"

    id: Optional[int] = Field(default=None, primary_key=True)

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")


class CandidateCreate(CandidateBase):
    """创建求职者的请求模型"""
    pass


class CandidateRead(CandidateBase):
    """读取求职者的响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime


class CandidateUpdate(SQLModel):
    """更新求职者的请求模型"""
    name: Optional[str] = None
    avatar: Optional[str] = None
    position: Optional[str] = None
    company: Optional[str] = None
    work_experience: Optional[str] = None
    education: Optional[str] = None
    expected_position: Optional[str] = None
    expected_salary: Optional[str] = None
    expected_location: Optional[str] = None
    status: Optional[CandidateStatus] = None
    active_time: Optional[datetime] = None
    last_contacted_at: Optional[datetime] = None
    profile_url: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None
