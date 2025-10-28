"""
自动化任务 API 路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime

from app.database import get_session
from app.models.automation_task import (
    AutomationTask,
    AutomationTaskCreate,
    AutomationTaskUpdate,
    TaskStatus
)
from app.models.greeting_template import GreetingTemplate
from app.services.boss_automation import BossAutomation
from app.services.logging_service import LoggingService
from app.models.log_entry import LogAction, LogLevel

router = APIRouter(prefix="/api/automation", tags=["automation"])

# 全局自动化服务实例（单例）
_automation_service: Optional[BossAutomation] = None
_current_task_id: Optional[int] = None


async def get_automation_service() -> BossAutomation:
    """获取或创建自动化服务实例"""
    global _automation_service
    if _automation_service is None:
        _automation_service = BossAutomation()
        await _automation_service.initialize(headless=False)
    return _automation_service


async def run_automation_task(task_id: int, session: AsyncSession):
    """
    在后台运行自动化任务

    Args:
        task_id: 任务 ID
        session: 数据库会话
    """
    global _current_task_id

    try:
        # 获取任务
        result = await session.execute(
            select(AutomationTask).where(AutomationTask.id == task_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            return

        # 更新任务状态
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        session.add(task)
        await session.commit()

        _current_task_id = task_id

        # 获取自动化服务
        automation = await get_automation_service()

        # 检查并登录
        if not automation.is_logged_in:
            is_logged_in = await automation.check_and_login()
            if not is_logged_in:
                task.status = TaskStatus.FAILED
                task.error_message = "登录失败"
                session.add(task)
                await session.commit()
                return

        # 获取问候模板
        template_result = await session.execute(
            select(GreetingTemplate).where(
                GreetingTemplate.id == task.greeting_template_id
            )
        )
        template = template_result.scalar_one_or_none()

        if not template:
            task.status = TaskStatus.FAILED
            task.error_message = "问候模板不存在"
            session.add(task)
            await session.commit()
            return

        # 解析筛选条件
        import json
        filters = json.loads(task.filters) if task.filters else {}

        # 搜索候选人
        candidates = await automation.search_candidates(
            keywords=task.search_keywords,
            city=filters.get('city'),
            experience=filters.get('experience'),
            degree=filters.get('degree'),
            max_results=task.max_contacts
        )

        task.total_found = len(candidates)
        session.add(task)
        await session.commit()

        # 向候选人发送问候
        from app.models.candidate import Candidate, CandidateStatus
        from app.models.greeting import GreetingRecord

        success_count = 0
        failed_count = 0

        for idx, candidate_data in enumerate(candidates):
            # 检查任务是否被暂停或取消
            await session.refresh(task)
            if task.status in [TaskStatus.PAUSED, TaskStatus.CANCELLED]:
                break

            # 检查是否已存在该候选人
            result = await session.execute(
                select(Candidate).where(Candidate.boss_id == candidate_data['boss_id'])
            )
            existing_candidate = result.scalar_one_or_none()

            if existing_candidate:
                # 检查是否已经联系过
                greeting_result = await session.execute(
                    select(GreetingRecord).where(
                        GreetingRecord.candidate_id == existing_candidate.id
                    )
                )
                if greeting_result.scalar_one_or_none():
                    continue  # 跳过已联系的候选人
                candidate = existing_candidate
            else:
                # 创建新候选人记录
                candidate = Candidate(
                    boss_id=candidate_data['boss_id'],
                    name=candidate_data['name'],
                    position=candidate_data['position'],
                    company=candidate_data.get('company'),
                    status=CandidateStatus.NEW,
                    profile_url=candidate_data.get('profile_url'),
                    active_time=candidate_data.get('active_time')
                )
                session.add(candidate)
                await session.commit()
                await session.refresh(candidate)

            # 生成个性化消息
            message = template.content
            message = message.replace('{name}', candidate.name)
            message = message.replace('{position}', candidate.position)
            if candidate.company:
                message = message.replace('{company}', candidate.company)

            # 发送问候
            send_success = await automation.send_greeting(
                candidate_boss_id=candidate.boss_id,
                message=message,
                use_random_delay=True
            )

            # 记录问候结果
            greeting_record = GreetingRecord(
                candidate_id=candidate.id,
                task_id=task.id,
                template_id=template.id,
                message=message,
                success=send_success,
                sent_at=datetime.now(),
                error_message=None if send_success else "发送失败"
            )
            session.add(greeting_record)

            # 更新候选人状态
            if send_success:
                candidate.status = CandidateStatus.CONTACTED
                success_count += 1
            else:
                failed_count += 1

            session.add(candidate)

            # 更新任务进度
            task.progress = int((idx + 1) / len(candidates) * 100)
            task.total_contacted = idx + 1
            task.total_success = success_count
            task.total_failed = failed_count
            session.add(task)

            await session.commit()

            # 检查是否出现问题
            issue = await automation.check_for_issues()
            if issue:
                task.status = TaskStatus.FAILED
                task.error_message = issue
                session.add(task)
                await session.commit()
                break

        # 任务完成
        if task.status == TaskStatus.RUNNING:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            session.add(task)
            await session.commit()

    except Exception as e:
        # 更新任务为失败状态
        result = await session.execute(
            select(AutomationTask).where(AutomationTask.id == task_id)
        )
        task = result.scalar_one_or_none()
        if task:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            session.add(task)
            await session.commit()

    finally:
        _current_task_id = None


@router.post("/tasks", response_model=AutomationTask)
async def create_task(
    task_data: AutomationTaskCreate,
    session: AsyncSession = Depends(get_session)
):
    """创建新的自动化任务"""
    # 验证模板是否存在
    result = await session.execute(
        select(GreetingTemplate).where(
            GreetingTemplate.id == task_data.greeting_template_id
        )
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="问候模板不存在")

    # 创建任务
    task = AutomationTask(
        **task_data.model_dump(),
        status=TaskStatus.PENDING,
        progress=0,
        total_found=0,
        total_contacted=0,
        total_success=0,
        total_failed=0,
        created_at=datetime.now()
    )

    session.add(task)
    await session.commit()
    await session.refresh(task)

    # 记录日志
    logging_service = LoggingService(session)
    await logging_service.log(
        action=LogAction.TASK_CREATE,
        message=f"创建任务: {task.name}",
        level=LogLevel.INFO,
        task_id=task.id,
        task_name=task.name,
        details={
            "search_keywords": task.search_keywords,
            "max_contacts": task.max_contacts,
            "template_id": task.greeting_template_id,
        }
    )

    return task


@router.get("/tasks", response_model=List[AutomationTask])
async def get_tasks(
    status: Optional[TaskStatus] = None,
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_session)
):
    """获取任务列表"""
    query = select(AutomationTask)

    if status:
        query = query.where(AutomationTask.status == status)

    query = query.order_by(AutomationTask.created_at.desc()).offset(offset).limit(limit)

    result = await session.execute(query)
    tasks = result.scalars().all()

    return tasks


@router.get("/tasks/{task_id}", response_model=AutomationTask)
async def get_task(
    task_id: int,
    session: AsyncSession = Depends(get_session)
):
    """获取任务详情"""
    result = await session.execute(
        select(AutomationTask).where(AutomationTask.id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return task


@router.post("/tasks/{task_id}/start")
async def start_task(
    task_id: int,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session)
):
    """启动任务"""
    global _current_task_id

    # 检查是否有其他任务正在运行
    if _current_task_id is not None:
        raise HTTPException(status_code=400, detail="已有任务正在运行")

    result = await session.execute(
        select(AutomationTask).where(AutomationTask.id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status not in [TaskStatus.PENDING, TaskStatus.PAUSED]:
        raise HTTPException(
            status_code=400,
            detail=f"任务状态为 {task.status}，无法启动"
        )

    # 记录日志
    logging_service = LoggingService(session)
    await logging_service.log(
        action=LogAction.TASK_START,
        message=f"启动任务: {task.name}",
        level=LogLevel.INFO,
        task_id=task.id,
        task_name=task.name,
    )

    # 在后台运行任务
    background_tasks.add_task(run_automation_task, task_id, session)

    return {"message": "任务已启动", "task_id": task_id}


@router.post("/tasks/{task_id}/pause")
async def pause_task(
    task_id: int,
    session: AsyncSession = Depends(get_session)
):
    """暂停任务"""
    result = await session.execute(
        select(AutomationTask).where(AutomationTask.id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status != TaskStatus.RUNNING:
        raise HTTPException(
            status_code=400,
            detail=f"任务状态为 {task.status}，无法暂停"
        )

    task.status = TaskStatus.PAUSED
    session.add(task)
    await session.commit()

    return {"message": "任务已暂停", "task_id": task_id}


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int,
    session: AsyncSession = Depends(get_session)
):
    """删除任务"""
    result = await session.execute(
        select(AutomationTask).where(AutomationTask.id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status == TaskStatus.RUNNING:
        raise HTTPException(status_code=400, detail="无法删除正在运行的任务")

    await session.delete(task)
    await session.commit()

    return {"message": "任务已删除", "task_id": task_id}


@router.post("/tasks/{task_id}/cancel")
async def cancel_task(
    task_id: int,
    session: AsyncSession = Depends(get_session)
):
    """取消任务"""
    result = await session.execute(
        select(AutomationTask).where(AutomationTask.id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status not in [TaskStatus.PENDING, TaskStatus.RUNNING, TaskStatus.PAUSED]:
        raise HTTPException(
            status_code=400,
            detail=f"任务状态为 {task.status}，无法取消"
        )

    task.status = TaskStatus.CANCELLED
    session.add(task)
    await session.commit()

    return {"message": "任务已取消", "task_id": task_id}


@router.get("/status")
async def get_automation_status():
    """获取自动化服务状态"""
    global _automation_service, _current_task_id

    return {
        "service_initialized": _automation_service is not None,
        "is_logged_in": _automation_service.is_logged_in if _automation_service else False,
        "current_task_id": _current_task_id
    }


@router.post("/login")
async def trigger_login():
    """触发登录流程"""
    automation = await get_automation_service()

    if automation.is_logged_in:
        return {"message": "已登录", "logged_in": True}

    # 启动登录流程
    is_logged_in = await automation.check_and_login()

    return {
        "message": "登录成功" if is_logged_in else "登录失败",
        "logged_in": is_logged_in
    }


@router.get("/qrcode")
async def get_qrcode():
    """获取登录二维码"""
    automation = await get_automation_service()

    if automation.is_logged_in:
        return {
            "success": False,
            "qrcode": "",
            "message": "已登录，无需扫码"
        }

    # 获取二维码
    result = await automation.get_qrcode()
    return result


@router.get("/check-login")
async def check_login(session: AsyncSession = Depends(get_session)):
    """检查登录状态并获取用户信息"""
    automation = await get_automation_service()

    # 检查登录状态
    result = await automation.check_login_status()

    # 如果登录成功，记录日志
    if result.get('logged_in'):
        user_info = result.get('user_info', {})
        logging_service = LoggingService(session)
        await logging_service.log(
            action=LogAction.LOGIN_SUCCESS,
            message=f"用户登录成功: {user_info.get('showName', 'Unknown')}",
            level=LogLevel.INFO,
            user_id=str(user_info.get('userId', '')),
            user_name=user_info.get('showName'),
            details={
                "email": user_info.get('email'),
                "company": user_info.get('brandName'),
            }
        )

    return result


@router.get("/refresh-qrcode")
async def refresh_qrcode():
    """检查并刷新二维码"""
    automation = await get_automation_service()

    # 检查并刷新二维码
    result = await automation.check_and_refresh_qrcode()
    return result


@router.post("/cleanup")
async def cleanup_service():
    """清理自动化服务"""
    global _automation_service, _current_task_id

    if _current_task_id is not None:
        raise HTTPException(status_code=400, detail="有任务正在运行，无法清理")

    if _automation_service:
        await _automation_service.cleanup()
        _automation_service = None

    return {"message": "服务已清理"}
