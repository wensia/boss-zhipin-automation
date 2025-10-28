"""
问候模板管理 API 路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime

from app.database import get_session
from app.models.greeting_template import (
    GreetingTemplate,
    GreetingTemplateCreate,
    GreetingTemplateUpdate
)
from app.models.automation_task import AutomationTask, TaskStatus

router = APIRouter(prefix="/api/templates", tags=["templates"])


@router.post("", response_model=GreetingTemplate)
async def create_template(
    template_data: GreetingTemplateCreate,
    session: AsyncSession = Depends(get_session)
):
    """创建问候模板"""
    template = GreetingTemplate(
        **template_data.model_dump(),
        usage_count=0,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    session.add(template)
    await session.commit()
    await session.refresh(template)

    return template


@router.get("", response_model=List[GreetingTemplate])
async def get_templates(
    is_active: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session)
):
    """获取模板列表"""
    query = select(GreetingTemplate)

    # 筛选激活状态
    if is_active is not None:
        query = query.where(GreetingTemplate.is_active == is_active)

    # 排序和分页
    query = query.order_by(
        GreetingTemplate.is_active.desc(),
        GreetingTemplate.updated_at.desc()
    ).offset(offset).limit(limit)

    result = await session.execute(query)
    templates = result.scalars().all()

    return templates


@router.get("/active", response_model=List[GreetingTemplate])
async def get_active_templates(session: AsyncSession = Depends(get_session)):
    """获取所有激活的模板"""
    result = await session.execute(
        select(GreetingTemplate)
        .where(GreetingTemplate.is_active == True)
        .order_by(GreetingTemplate.usage_count.desc())
    )
    templates = result.scalars().all()

    return templates


@router.get("/{template_id}", response_model=GreetingTemplate)
async def get_template(
    template_id: int,
    session: AsyncSession = Depends(get_session)
):
    """获取模板详情"""
    result = await session.execute(
        select(GreetingTemplate).where(GreetingTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    return template


@router.patch("/{template_id}", response_model=GreetingTemplate)
async def update_template(
    template_id: int,
    template_data: GreetingTemplateUpdate,
    session: AsyncSession = Depends(get_session)
):
    """更新模板"""
    result = await session.execute(
        select(GreetingTemplate).where(GreetingTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    # 更新字段
    update_data = template_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)

    template.updated_at = datetime.now()

    session.add(template)
    await session.commit()
    await session.refresh(template)

    return template


@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    session: AsyncSession = Depends(get_session)
):
    """删除模板"""
    result = await session.execute(
        select(GreetingTemplate).where(GreetingTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    # 检查是否有正在使用该模板的任务
    task_result = await session.execute(
        select(AutomationTask).where(
            (AutomationTask.greeting_template_id == template_id) &
            (AutomationTask.status.in_([TaskStatus.PENDING, TaskStatus.RUNNING]))
        )
    )
    active_tasks = task_result.scalars().all()

    if active_tasks:
        raise HTTPException(
            status_code=400,
            detail="有任务正在使用该模板，无法删除"
        )

    await session.delete(template)
    await session.commit()

    return {"message": "模板已删除", "template_id": template_id}


@router.post("/{template_id}/activate")
async def activate_template(
    template_id: int,
    session: AsyncSession = Depends(get_session)
):
    """激活模板"""
    result = await session.execute(
        select(GreetingTemplate).where(GreetingTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    template.is_active = True
    template.updated_at = datetime.now()

    session.add(template)
    await session.commit()

    return {"message": "模板已激活", "template_id": template_id}


@router.post("/{template_id}/deactivate")
async def deactivate_template(
    template_id: int,
    session: AsyncSession = Depends(get_session)
):
    """停用模板"""
    result = await session.execute(
        select(GreetingTemplate).where(GreetingTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    # 检查是否有正在使用该模板的任务
    task_result = await session.execute(
        select(AutomationTask).where(
            (AutomationTask.greeting_template_id == template_id) &
            (AutomationTask.status.in_([TaskStatus.PENDING, TaskStatus.RUNNING]))
        )
    )
    active_tasks = task_result.scalars().all()

    if active_tasks:
        raise HTTPException(
            status_code=400,
            detail="有任务正在使用该模板，无法停用"
        )

    template.is_active = False
    template.updated_at = datetime.now()

    session.add(template)
    await session.commit()

    return {"message": "模板已停用", "template_id": template_id}


@router.post("/{template_id}/duplicate", response_model=GreetingTemplate)
async def duplicate_template(
    template_id: int,
    session: AsyncSession = Depends(get_session)
):
    """复制模板"""
    result = await session.execute(
        select(GreetingTemplate).where(GreetingTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    # 创建副本
    new_template = GreetingTemplate(
        name=f"{template.name} (副本)",
        content=template.content,
        is_active=False,  # 副本默认不激活
        usage_count=0,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    session.add(new_template)
    await session.commit()
    await session.refresh(new_template)

    return new_template


@router.get("/{template_id}/preview")
async def preview_template(
    template_id: int,
    name: str = Query(..., description="候选人姓名"),
    position: str = Query(..., description="职位"),
    company: Optional[str] = Query(None, description="公司"),
    session: AsyncSession = Depends(get_session)
):
    """预览模板效果"""
    result = await session.execute(
        select(GreetingTemplate).where(GreetingTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    # 生成预览内容
    preview_content = template.content
    preview_content = preview_content.replace('{name}', name)
    preview_content = preview_content.replace('{position}', position)
    if company:
        preview_content = preview_content.replace('{company}', company)

    return {
        "template_id": template_id,
        "template_name": template.name,
        "original_content": template.content,
        "preview_content": preview_content,
        "variables_used": {
            "name": name,
            "position": position,
            "company": company
        }
    }


@router.post("/batch/delete")
async def batch_delete_templates(
    template_ids: List[int],
    session: AsyncSession = Depends(get_session)
):
    """批量删除模板"""
    result = await session.execute(
        select(GreetingTemplate).where(GreetingTemplate.id.in_(template_ids))
    )
    templates = result.scalars().all()

    if not templates:
        raise HTTPException(status_code=404, detail="未找到任何模板")

    # 检查是否有正在使用的模板
    for template in templates:
        task_result = await session.execute(
            select(AutomationTask).where(
                (AutomationTask.greeting_template_id == template.id) &
                (AutomationTask.status.in_([TaskStatus.PENDING, TaskStatus.RUNNING]))
            )
        )
        if task_result.scalars().first():
            raise HTTPException(
                status_code=400,
                detail=f"模板 {template.name} 正在被任务使用，无法删除"
            )

    deleted_count = 0
    for template in templates:
        await session.delete(template)
        deleted_count += 1

    await session.commit()

    return {
        "message": f"已删除 {deleted_count} 个模板",
        "deleted_count": deleted_count
    }
