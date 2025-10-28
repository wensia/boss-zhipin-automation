"""
示例路由
根据实际需求修改此文件
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_session
from app.models.example import Job, JobCreate, JobRead, JobUpdate

router = APIRouter()


@router.get("/jobs", response_model=list[JobRead])
async def get_jobs(session: AsyncSession = Depends(get_session)):
    """获取所有职位"""
    result = await session.execute(select(Job))
    jobs = result.scalars().all()
    return jobs


@router.get("/jobs/{job_id}", response_model=JobRead)
async def get_job(job_id: int, session: AsyncSession = Depends(get_session)):
    """获取单个职位"""
    job = await session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    return job


@router.post("/jobs", response_model=JobRead)
async def create_job(job: JobCreate, session: AsyncSession = Depends(get_session)):
    """创建新职位"""
    db_job = Job.model_validate(job)
    session.add(db_job)
    await session.commit()
    await session.refresh(db_job)
    return db_job


@router.patch("/jobs/{job_id}", response_model=JobRead)
async def update_job(
    job_id: int,
    job_update: JobUpdate,
    session: AsyncSession = Depends(get_session)
):
    """更新职位信息"""
    job = await session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")

    job_data = job_update.model_dump(exclude_unset=True)
    for key, value in job_data.items():
        setattr(job, key, value)

    session.add(job)
    await session.commit()
    await session.refresh(job)
    return job


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: int, session: AsyncSession = Depends(get_session)):
    """删除职位"""
    job = await session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")

    await session.delete(job)
    await session.commit()
    return {"message": "职位删除成功"}
