"""
自动化流程模板管理API路由
用于保存和管理完整的自动化流程配置
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from app.database import get_session
from app.models.automation_template import (
    AutomationTemplate,
    AutomationTemplateCreate,
    AutomationTemplateUpdate,
    AutomationTemplateRead
)

router = APIRouter(prefix="/api/automation-templates", tags=["automation-templates"])


@router.post("", response_model=AutomationTemplateRead, summary="创建自动化模板")
async def create_template(
    template: AutomationTemplateCreate,
    session: Session = Depends(get_session)
):
    """
    创建新的自动化流程模板
    """
    db_template = AutomationTemplate.model_validate(template)
    session.add(db_template)
    await session.commit()
    await session.refresh(db_template)
    return db_template


@router.get("", response_model=List[AutomationTemplateRead], summary="获取所有模板")
async def get_templates(
    account_id: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """获取所有自动化流程模板列表"""
    query = select(AutomationTemplate)
    
    if account_id is not None:
        query = query.where(AutomationTemplate.account_id == account_id)
    
    query = query.order_by(AutomationTemplate.updated_at.desc())
    
    result = await session.execute(query)
    templates = result.scalars().all()
    return templates


@router.get("/{template_id}", response_model=AutomationTemplateRead, summary="获取模板详情")
async def get_template(
    template_id: int,
    session: Session = Depends(get_session)
):
    """获取指定ID的模板详情"""
    template = await session.get(AutomationTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return template


@router.put("/{template_id}", response_model=AutomationTemplateRead, summary="更新模板")
async def update_template(
    template_id: int,
    template_update: AutomationTemplateUpdate,
    session: Session = Depends(get_session)
):
    """更新指定ID的模板配置"""
    db_template = await session.get(AutomationTemplate, template_id)
    if not db_template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 更新字段
    update_data = template_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_template, key, value)
    
    # 更新修改时间
    db_template.updated_at = datetime.now()
    
    session.add(db_template)
    await session.commit()
    await session.refresh(db_template)
    return db_template


@router.delete("/{template_id}", summary="删除模板")
async def delete_template(
    template_id: int,
    session: Session = Depends(get_session)
):
    """删除指定ID的模板"""
    template = await session.get(AutomationTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    await session.delete(template)
    await session.commit()
    
    return {"success": True, "message": "模板已删除"}


@router.post("/{template_id}/use", response_model=AutomationTemplateRead, summary="使用模板")
async def use_template(
    template_id: int,
    session: Session = Depends(get_session)
):
    """标记模板为已使用，更新使用次数和最后使用时间"""
    template = await session.get(AutomationTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 更新使用统计
    template.usage_count += 1
    template.last_used_at = datetime.now()
    
    session.add(template)
    await session.commit()
    await session.refresh(template)
    
    return template


@router.post("/{template_id}/duplicate", response_model=AutomationTemplateRead, summary="复制模板")
async def duplicate_template(
    template_id: int,
    new_name: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """复制现有模板创建新模板"""
    template = await session.get(AutomationTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 创建副本
    new_template = AutomationTemplate(
        name=new_name or f"{template.name} (副本)",
        description=template.description,
        account_id=template.account_id,
        headless=template.headless,
        job_id=template.job_id,
        job_name=template.job_name,
        filters=template.filters,
        greeting_count=template.greeting_count,
        expected_positions=template.expected_positions,
        usage_count=0
    )
    
    session.add(new_template)
    await session.commit()
    await session.refresh(new_template)
    
    return new_template


@router.get("/stats/summary", summary="获取模板统计信息")
async def get_template_stats(
    session: Session = Depends(get_session)
):
    """获取模板的统计信息"""
    # 总数
    count_query = select(AutomationTemplate)
    result = await session.execute(count_query)
    total_count = len(result.scalars().all())
    
    # 最常用的模板
    most_used_query = select(AutomationTemplate).order_by(
        AutomationTemplate.usage_count.desc()
    ).limit(5)
    result = await session.execute(most_used_query)
    most_used = result.scalars().all()
    
    # 最近使用的模板
    recent_query = select(AutomationTemplate).where(
        AutomationTemplate.last_used_at.isnot(None)
    ).order_by(
        AutomationTemplate.last_used_at.desc()
    ).limit(5)
    result = await session.execute(recent_query)
    recently_used = result.scalars().all()
    
    return {
        "total_count": total_count,
        "most_used": [
            {
                "id": t.id,
                "name": t.name,
                "usage_count": t.usage_count,
                "account_id": t.account_id
            }
            for t in most_used
        ],
        "recently_used": [
            {
                "id": t.id,
                "name": t.name,
                "last_used_at": t.last_used_at.isoformat() if t.last_used_at else None,
                "account_id": t.account_id
            }
            for t in recently_used
        ]
    }
