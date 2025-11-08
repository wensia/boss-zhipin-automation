"""
筛选条件数据模型
"""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class AgeFilter(BaseModel):
    """年龄筛选"""
    min: int = Field(22, ge=16, le=60, description="最小年龄")
    max: Optional[int] = Field(40, ge=16, le=60, description="最大年龄，None表示不限")

    @field_validator('max')
    @classmethod
    def validate_age_range(cls, v, info):
        """验证最大年龄不能小于最小年龄"""
        if v is not None:
            min_age = info.data.get('min', 22)
            if v < min_age:
                raise ValueError(f'最大年龄 ({v}) 不能小于最小年龄 ({min_age})')
        return v


class FilterOptions(BaseModel):
    """完整的筛选条件"""

    # 年龄范围
    age: Optional[AgeFilter] = Field(None, description="年龄范围")

    # 专业（可多选）
    major: Optional[List[str]] = Field(None, description="专业")

    # 活跃度（单选）
    activity: Optional[str] = Field(None, description="活跃度")

    # 性别（可多选）
    gender: Optional[List[str]] = Field(None, description="性别")

    # 近期没有看过（可多选）
    not_recently_viewed: Optional[List[str]] = Field(None, description="近期没有看过")

    # 是否与同事交换简历（可多选）
    resume_exchange: Optional[List[str]] = Field(None, description="是否与同事交换简历")

    # 院校（可多选）
    school: Optional[List[str]] = Field(None, description="院校")

    # 跳槽频率（单选）
    job_hopping_frequency: Optional[str] = Field(None, description="跳槽频率")

    # 牛人关键词（可多选）
    keywords: Optional[List[str]] = Field(None, description="牛人关键词")

    # 经验要求（可多选）
    experience: Optional[List[str]] = Field(None, description="经验要求")

    # 学历要求（可多选）
    education: Optional[List[str]] = Field(None, description="学历要求")

    # 薪资待遇（单选）
    salary: Optional[str] = Field(None, description="薪资待遇")

    # 求职意向（可多选）
    job_intention: Optional[List[str]] = Field(None, description="求职意向")


# 筛选条件的映射配置
FILTER_SELECTORS = {
    "major": ".filter-item .major",  # 专业选择器
    "activity": ".filter-item.activity",  # 活跃度选择器
    "gender": ".filter-item.gender",  # 性别选择器
    "not_recently_viewed": ".filter-item .not-recently-viewed",
    "resume_exchange": ".filter-item .resume-exchange",
    "school": ".filter-item.school",
    "job_hopping_frequency": ".filter-item .job-hopping",
    "keywords": ".filter-item .keywords",
    "experience": ".filter-item.experience",
    "education": ".filter-item.education",
    "salary": ".filter-item.salary",
    "job_intention": ".filter-item .job-intention",
}
