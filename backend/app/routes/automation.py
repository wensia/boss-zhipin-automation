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
from app.models.filters import FilterOptions
from app.models.system_config import SystemConfig
from app.models.user_account import UserAccount
from app.services.boss_automation import BossAutomation
from app.services.logging_service import LoggingService
from app.models.log_entry import LogAction, LogLevel
from app.utils.filters_applier import FiltersApplier

router = APIRouter(prefix="/api/automation", tags=["automation"])

# 全局自动化服务实例（单例）
_automation_service: Optional[BossAutomation] = None
_current_task_id: Optional[int] = None
_headless: bool = True  # 默认隐藏浏览器


async def get_automation_service(headless: Optional[bool] = None) -> BossAutomation:
    """获取或创建自动化服务实例

    Args:
        headless: 是否无头模式，None 则使用全局设置
    """
    global _automation_service, _headless

    # 如果指定了 headless 参数，更新全局设置
    if headless is not None:
        _headless = headless

    if _automation_service is None:
        _automation_service = BossAutomation()
        await _automation_service.initialize(headless=_headless)
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

        # 获取问候模板（如果指定）
        template = None
        if task.greeting_template_id is not None:
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
            if template:
                message = template.content
                message = message.replace('{name}', candidate.name)
                message = message.replace('{position}', candidate.position)
                if candidate.company:
                    message = message.replace('{company}', candidate.company)
            else:
                # 使用默认消息
                message = f"你好，我对你的简历很感兴趣，期待与你进一步沟通。"

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
                template_id=template.id if template else None,
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
    # 如果指定了模板ID，验证模板是否存在
    if task_data.greeting_template_id is not None:
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
    global _automation_service, _current_task_id, _headless

    return {
        "service_initialized": _automation_service is not None,
        "is_logged_in": _automation_service.is_logged_in if _automation_service else False,
        "current_task_id": _current_task_id,
        "headless": _headless
    }


@router.post("/init")
async def initialize_browser(
    headless: bool = True,
    com_id: Optional[int] = None
):
    """初始化浏览器

    Args:
        headless: 是否无头模式（隐藏浏览器窗口）
        com_id: 可选的账号com_id，用于加载该账号的登录状态

    Returns:
        初始化结果
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"🔧 初始化浏览器 - headless={headless} (类型: {type(headless).__name__}), com_id={com_id}")

    global _automation_service, _headless

    # 如果已经初始化，先清理
    if _automation_service is not None:
        await _automation_service.cleanup()
        _automation_service = None

    # 设置 headless 模式
    _headless = headless
    logger.info(f"🔧 设置全局 _headless={_headless}")

    # 创建自动化服务实例，如果指定了com_id则使用该账号
    _automation_service = BossAutomation(com_id=com_id)
    await _automation_service.initialize(headless=headless)

    return {
        "success": True,
        "message": f"浏览器初始化成功{f'（使用账号 {com_id}）' if com_id else ''}",
        "headless": headless,
        "service_initialized": True,
        "com_id": com_id
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

    # 直接调用 get_qrcode，让它自己判断是否需要二维码
    # 不在路由层面检查 is_logged_in，因为这个标志可能过期
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


@router.get("/jobs")
async def get_chatted_jobs():
    """获取已沟通的职位列表"""
    automation = await get_automation_service()

    # 获取职位列表
    result = await automation.get_chatted_jobs()
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


@router.get("/recommend-candidates")
async def get_recommend_candidates(
    max_results: int = 50,
    session: AsyncSession = Depends(get_session)
):
    """获取推荐候选人列表

    Args:
        max_results: 最大候选人数量（默认 50）

    Returns:
        推荐候选人列表
    """
    automation = await get_automation_service()

    if not automation.is_logged_in:
        raise HTTPException(status_code=401, detail="未登录，无法获取推荐候选人")

    try:
        # 获取推荐候选人
        candidates = await automation.get_recommended_candidates(max_results=max_results)

        # 记录日志
        logging_service = LoggingService(session)
        await logging_service.log(
            action=LogAction.SEARCH,
            message=f"获取推荐候选人列表，返回 {len(candidates)} 个结果",
            level=LogLevel.INFO,
            details={
                "max_results": max_results,
                "actual_results": len(candidates)
            }
        )

        return {
            "success": True,
            "count": len(candidates),
            "candidates": candidates
        }

    except Exception as e:
        # 记录错误日志
        logging_service = LoggingService(session)
        await logging_service.log(
            action=LogAction.ERROR,
            message=f"获取推荐候选人失败: {str(e)}",
            level=LogLevel.ERROR,
            details={"error": str(e)}
        )

        raise HTTPException(
            status_code=500,
            detail=f"获取推荐候选人失败: {str(e)}"
        )


@router.get("/available-jobs")
async def get_available_jobs(session: AsyncSession = Depends(get_session)):
    """获取当前可用的招聘职位列表

    Returns:
        职位列表
    """
    automation = await get_automation_service()

    if not automation.is_logged_in:
        raise HTTPException(status_code=401, detail="未登录，无法获取职位列表")

    try:
        # 获取可用职位
        result = await automation.get_available_jobs()

        # 记录日志
        if result.get('success'):
            logging_service = LoggingService(session)
            await logging_service.log(
                action=LogAction.SEARCH,
                message=f"获取可用职位列表，返回 {result.get('total', 0)} 个职位",
                level=LogLevel.INFO,
                details={
                    "total_jobs": result.get('total', 0)
                }
            )

        return result

    except Exception as e:
        # 记录错误日志
        logging_service = LoggingService(session)
        await logging_service.log(
            action=LogAction.ERROR,
            message=f"获取职位列表失败: {str(e)}",
            level=LogLevel.ERROR,
            details={"error": str(e)}
        )

        raise HTTPException(
            status_code=500,
            detail=f"获取职位列表失败: {str(e)}"
        )


@router.post("/select-job")
async def select_job(
    job_value: str,
    session: AsyncSession = Depends(get_session)
):
    """选择指定的招聘职位

    Args:
        job_value: 职位的 value 属性值

    Returns:
        选择结果
    """
    automation = await get_automation_service()

    if not automation.is_logged_in:
        raise HTTPException(status_code=401, detail="未登录，无法选择职位")

    try:
        # 选择职位
        result = await automation.select_job_position(job_value=job_value)

        # 记录日志
        if result.get('success'):
            logging_service = LoggingService(session)
            await logging_service.log(
                action=LogAction.SEARCH,
                message=f"选择职位成功: {job_value}",
                level=LogLevel.INFO,
                details={
                    "job_value": job_value
                }
            )
        else:
            logging_service = LoggingService(session)
            await logging_service.log(
                action=LogAction.ERROR,
                message=f"选择职位失败: {result.get('message')}",
                level=LogLevel.WARNING,
                details={
                    "job_value": job_value,
                    "error": result.get('message')
                }
            )

        return result

    except Exception as e:
        # 记录错误日志
        logging_service = LoggingService(session)
        await logging_service.log(
            action=LogAction.ERROR,
            message=f"选择职位失败: {str(e)}",
            level=LogLevel.ERROR,
            details={
                "job_value": job_value,
                "error": str(e)
            }
        )

        raise HTTPException(
            status_code=500,
            detail=f"选择职位失败: {str(e)}"
        )


@router.post("/apply-filters")
async def apply_filters(
    filters: FilterOptions,
    session: AsyncSession = Depends(get_session)
):
    """应用筛选条件到推荐页面

    Args:
        filters: 筛选条件对象

    Returns:
        应用结果
    """
    automation = await get_automation_service()

    if not automation.is_logged_in:
        raise HTTPException(status_code=401, detail="未登录，无法应用筛选条件")

    try:
        import asyncio

        # 导航到推荐页面
        await automation.navigate_to_recommend_page()
        await asyncio.sleep(3)

        # 获取 iframe
        recommend_frame = None
        for frame in automation.page.frames:
            if frame.name == 'recommendFrame':
                recommend_frame = frame
                break

        if not recommend_frame:
            raise HTTPException(status_code=500, detail="未找到推荐页面 iframe")

        # 应用筛选条件
        applier = FiltersApplier(recommend_frame, automation.page)

        # 打开筛选面板
        if not await applier.open_filter_panel():
            raise HTTPException(status_code=500, detail="无法打开筛选面板")

        # 应用所有筛选条件
        filter_result = await applier.apply_all_filters(filters)

        if not filter_result['success']:
            raise HTTPException(
                status_code=500,
                detail=f"筛选条件应用失败: {filter_result.get('error', 'Unknown error')}"
            )

        # 记录日志
        logging_service = LoggingService(session)
        await logging_service.log(
            action=LogAction.SEARCH,
            message=f"应用筛选条件成功: {len(filter_result['applied_filters'])} 项",
            level=LogLevel.INFO,
            details={
                "applied_filters": filter_result['applied_filters'],
                "failed_filters": filter_result['failed_filters']
            }
        )

        return {
            "success": True,
            "message": f"成功应用 {len(filter_result['applied_filters'])} 项筛选条件",
            "applied_count": len(filter_result['applied_filters']),
            "failed_count": len(filter_result['failed_filters']),
            "details": filter_result
        }

    except HTTPException:
        raise
    except Exception as e:
        # 记录错误日志
        logging_service = LoggingService(session)
        await logging_service.log(
            action=LogAction.ERROR,
            message=f"应用筛选条件失败: {str(e)}",
            level=LogLevel.ERROR,
            details={"error": str(e)}
        )

        raise HTTPException(
            status_code=500,
            detail=f"应用筛选条件失败: {str(e)}"
        )


@router.post("/switch-account/{account_id}")
async def switch_automation_account(
    account_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    切换自动化服务使用的账号

    Args:
        account_id: 要切换到的账号ID
        session: 数据库会话

    Returns:
        切换结果
    """
    try:
        # 获取账号信息
        result = await session.execute(
            select(UserAccount).where(UserAccount.id == account_id)
        )
        account = result.scalar_one_or_none()

        if not account:
            raise HTTPException(status_code=404, detail="账号不存在")

        # 获取自动化服务
        automation = await get_automation_service()

        if not automation:
            raise HTTPException(status_code=500, detail="自动化服务未初始化")

        # 执行账号切换
        switch_result = await automation.switch_account(account.com_id)

        if not switch_result.get('success'):
            # 切换失败
            return {
                "success": False,
                "message": switch_result.get('message', '切换失败'),
                "needs_login": switch_result.get('needs_login', False)
            }

        # 切换成功，更新系统配置中的当前账号ID
        config_result = await session.execute(select(SystemConfig))
        config = config_result.scalar_one_or_none()

        if not config:
            config = SystemConfig()
            session.add(config)

        config.current_account_id = account_id
        config.updated_at = datetime.now()
        await session.commit()

        # 记录日志
        logging_service = LoggingService(session)
        await logging_service.log(
            action=LogAction.SYSTEM,
            message=f"切换账号成功: {account.show_name}",
            level=LogLevel.INFO,
            details={
                "account_id": account_id,
                "com_id": account.com_id,
                "show_name": account.show_name
            }
        )

        return {
            "success": True,
            "message": "账号切换成功",
            "account": {
                "id": account.id,
                "com_id": account.com_id,
                "show_name": account.show_name,
                "avatar": account.avatar,
                "company_name": account.company_short_name
            },
            "user_info": switch_result.get('user_info')
        }

    except HTTPException:
        raise
    except Exception as e:
        # 记录错误日志
        logging_service = LoggingService(session)
        await logging_service.log(
            action=LogAction.ERROR,
            message=f"切换账号失败: {str(e)}",
            level=LogLevel.ERROR,
            details={"error": str(e), "account_id": account_id}
        )

        raise HTTPException(
            status_code=500,
            detail=f"切换账号失败: {str(e)}"
        )
