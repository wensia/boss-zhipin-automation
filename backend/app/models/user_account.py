"""
Boss直聘用户账号模型
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class UserAccountBase(SQLModel):
    """用户账号基础模型"""
    com_id: int = Field(
        index=True,
        unique=True,
        description="公司ID，作为唯一索引"
    )
    name: str = Field(description="用户真实姓名")
    show_name: str = Field(description="显示名称")
    gender: int = Field(description="性别: 0未知, 1男, 2女")
    avatar: str = Field(description="头像URL")
    title: str = Field(description="职位")

    # 公司信息
    company_name: str = Field(description="公司全称")
    company_short_name: str = Field(description="公司简称")
    brand_id: int = Field(description="品牌ID")
    encrypt_brand_id: str = Field(description="加密品牌ID")
    company_logo: str = Field(description="公司Logo URL")
    industry: str = Field(description="所属行业")

    # 联系信息
    resume_email: Optional[str] = Field(default=None, description="简历邮箱")
    weixin: Optional[str] = Field(default=None, description="微信号")

    # 认证信息
    cert: bool = Field(default=False, description="是否已认证")
    cert_gender: int = Field(description="认证性别")
    is_gold: int = Field(default=0, description="是否为金牌猎头")

    # 原始数据
    raw_data: str = Field(description="API返回的原始JSON数据")

    # 登录状态文件路径
    auth_file_path: Optional[str] = Field(
        default=None,
        description="登录状态存储文件路径"
    )

    # 时间戳
    last_login_at: datetime = Field(
        default_factory=datetime.now,
        description="上次登录时间"
    )


class UserAccount(UserAccountBase, table=True):
    """用户账号表"""
    __tablename__ = "user_accounts"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="更新时间"
    )


class UserAccountCreate(UserAccountBase):
    """创建用户账号"""
    pass


class UserAccountUpdate(SQLModel):
    """更新用户账号"""
    name: Optional[str] = None
    show_name: Optional[str] = None
    avatar: Optional[str] = None
    title: Optional[str] = None
    company_name: Optional[str] = None
    company_short_name: Optional[str] = None
    company_logo: Optional[str] = None
    industry: Optional[str] = None
    resume_email: Optional[str] = None
    weixin: Optional[str] = None
    cert: Optional[bool] = None
    is_gold: Optional[int] = None
    raw_data: Optional[str] = None
    auth_file_path: Optional[str] = None
    last_login_at: Optional[datetime] = None


class UserAccountRead(UserAccountBase):
    """读取用户账号"""
    id: int
    created_at: datetime
    updated_at: datetime
