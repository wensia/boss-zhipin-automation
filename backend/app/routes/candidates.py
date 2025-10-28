"""
候选人管理 API 路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func
from datetime import datetime

from app.database import get_session
from app.models.candidate import (
    Candidate,
    CandidateCreate,
    CandidateUpdate,
    CandidateStatus
)
from app.models.greeting import GreetingRecord

router = APIRouter(prefix="/api/candidates", tags=["candidates"])


@router.post("", response_model=Candidate)
async def create_candidate(
    candidate_data: CandidateCreate,
    session: AsyncSession = Depends(get_session)
):
    """创建候选人"""
    # 检查是否已存在
    result = await session.execute(
        select(Candidate).where(Candidate.boss_id == candidate_data.boss_id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="该候选人已存在")

    candidate = Candidate(
        **candidate_data.model_dump(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    session.add(candidate)
    await session.commit()
    await session.refresh(candidate)

    return candidate


@router.get("", response_model=List[Candidate])
async def get_candidates(
    status: Optional[CandidateStatus] = None,
    search: Optional[str] = Query(None, description="搜索关键词（姓名、职位、公司）"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session)
):
    """获取候选人列表"""
    query = select(Candidate)

    # 状态筛选
    if status:
        query = query.where(Candidate.status == status)

    # 关键词搜索
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (Candidate.name.like(search_pattern)) |
            (Candidate.position.like(search_pattern)) |
            (Candidate.company.like(search_pattern))
        )

    # 分页
    query = query.order_by(Candidate.created_at.desc()).offset(offset).limit(limit)

    result = await session.execute(query)
    candidates = result.scalars().all()

    return candidates


@router.get("/stats")
async def get_candidate_stats(session: AsyncSession = Depends(get_session)):
    """获取候选人统计信息"""
    # 按状态统计
    status_stats = {}
    for status in CandidateStatus:
        result = await session.execute(
            select(func.count(Candidate.id)).where(Candidate.status == status)
        )
        count = result.scalar()
        status_stats[status.value] = count

    # 总数
    total_result = await session.execute(select(func.count(Candidate.id)))
    total = total_result.scalar()

    # 今日新增
    from datetime import date
    today = date.today()
    today_result = await session.execute(
        select(func.count(Candidate.id)).where(
            func.date(Candidate.created_at) == today
        )
    )
    today_count = today_result.scalar()

    return {
        "total": total,
        "today_added": today_count,
        "by_status": status_stats
    }


@router.get("/{candidate_id}", response_model=Candidate)
async def get_candidate(
    candidate_id: int,
    session: AsyncSession = Depends(get_session)
):
    """获取候选人详情"""
    result = await session.execute(
        select(Candidate).where(Candidate.id == candidate_id)
    )
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(status_code=404, detail="候选人不存在")

    return candidate


@router.patch("/{candidate_id}", response_model=Candidate)
async def update_candidate(
    candidate_id: int,
    candidate_data: CandidateUpdate,
    session: AsyncSession = Depends(get_session)
):
    """更新候选人信息"""
    result = await session.execute(
        select(Candidate).where(Candidate.id == candidate_id)
    )
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(status_code=404, detail="候选人不存在")

    # 更新字段
    update_data = candidate_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(candidate, field, value)

    candidate.updated_at = datetime.now()

    session.add(candidate)
    await session.commit()
    await session.refresh(candidate)

    return candidate


@router.delete("/{candidate_id}")
async def delete_candidate(
    candidate_id: int,
    session: AsyncSession = Depends(get_session)
):
    """删除候选人"""
    result = await session.execute(
        select(Candidate).where(Candidate.id == candidate_id)
    )
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(status_code=404, detail="候选人不存在")

    # 检查是否有关联的问候记录
    greeting_result = await session.execute(
        select(GreetingRecord).where(GreetingRecord.candidate_id == candidate_id)
    )
    greeting_records = greeting_result.scalars().all()

    if greeting_records:
        raise HTTPException(
            status_code=400,
            detail="该候选人有关联的问候记录，无法删除"
        )

    await session.delete(candidate)
    await session.commit()

    return {"message": "候选人已删除", "candidate_id": candidate_id}


@router.get("/{candidate_id}/greetings", response_model=List[GreetingRecord])
async def get_candidate_greetings(
    candidate_id: int,
    session: AsyncSession = Depends(get_session)
):
    """获取候选人的问候记录"""
    # 检查候选人是否存在
    candidate_result = await session.execute(
        select(Candidate).where(Candidate.id == candidate_id)
    )
    candidate = candidate_result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(status_code=404, detail="候选人不存在")

    # 获取问候记录
    result = await session.execute(
        select(GreetingRecord)
        .where(GreetingRecord.candidate_id == candidate_id)
        .order_by(GreetingRecord.sent_at.desc())
    )
    greetings = result.scalars().all()

    return greetings


@router.post("/{candidate_id}/archive")
async def archive_candidate(
    candidate_id: int,
    session: AsyncSession = Depends(get_session)
):
    """归档候选人"""
    result = await session.execute(
        select(Candidate).where(Candidate.id == candidate_id)
    )
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(status_code=404, detail="候选人不存在")

    candidate.status = CandidateStatus.ARCHIVED
    candidate.updated_at = datetime.now()

    session.add(candidate)
    await session.commit()

    return {"message": "候选人已归档", "candidate_id": candidate_id}


@router.post("/batch/update-status")
async def batch_update_status(
    candidate_ids: List[int],
    status: CandidateStatus,
    session: AsyncSession = Depends(get_session)
):
    """批量更新候选人状态"""
    result = await session.execute(
        select(Candidate).where(Candidate.id.in_(candidate_ids))
    )
    candidates = result.scalars().all()

    if not candidates:
        raise HTTPException(status_code=404, detail="未找到任何候选人")

    updated_count = 0
    for candidate in candidates:
        candidate.status = status
        candidate.updated_at = datetime.now()
        session.add(candidate)
        updated_count += 1

    await session.commit()

    return {
        "message": f"已更新 {updated_count} 个候选人状态",
        "updated_count": updated_count
    }


@router.post("/batch/delete")
async def batch_delete_candidates(
    candidate_ids: List[int],
    session: AsyncSession = Depends(get_session)
):
    """批量删除候选人"""
    result = await session.execute(
        select(Candidate).where(Candidate.id.in_(candidate_ids))
    )
    candidates = result.scalars().all()

    if not candidates:
        raise HTTPException(status_code=404, detail="未找到任何候选人")

    # 检查是否有问候记录
    for candidate in candidates:
        greeting_result = await session.execute(
            select(GreetingRecord).where(
                GreetingRecord.candidate_id == candidate.id
            )
        )
        if greeting_result.scalars().first():
            raise HTTPException(
                status_code=400,
                detail=f"候选人 {candidate.name} 有关联的问候记录，无法删除"
            )

    deleted_count = 0
    for candidate in candidates:
        await session.delete(candidate)
        deleted_count += 1

    await session.commit()

    return {
        "message": f"已删除 {deleted_count} 个候选人",
        "deleted_count": deleted_count
    }
