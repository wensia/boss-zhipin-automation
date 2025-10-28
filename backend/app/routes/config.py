"""
系统配置 API 路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime, date

from app.database import get_session
from app.models.system_config import SystemConfig, SystemConfigUpdate

router = APIRouter(prefix="/api/config", tags=["config"])


async def get_or_create_config(session: AsyncSession) -> SystemConfig:
    """获取或创建系统配置（单例模式）"""
    result = await session.execute(select(SystemConfig))
    config = result.scalar_one_or_none()

    if not config:
        # 创建默认配置
        config = SystemConfig(
            id=1,
            boss_username=None,
            boss_session_saved=False,
            auto_mode_enabled=False,
            daily_limit=100,
            today_contacted=0,
            anti_detection_enabled=True,
            random_delay_enabled=True,
            rest_interval=15,
            rest_duration=60,
            last_contact_time=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(config)
        await session.commit()
        await session.refresh(config)

    return config


@router.get("", response_model=SystemConfig)
async def get_config(session: AsyncSession = Depends(get_session)):
    """获取系统配置"""
    config = await get_or_create_config(session)
    return config


@router.patch("", response_model=SystemConfig)
async def update_config(
    config_data: SystemConfigUpdate,
    session: AsyncSession = Depends(get_session)
):
    """更新系统配置"""
    config = await get_or_create_config(session)

    # 更新字段
    update_data = config_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)

    config.updated_at = datetime.now()

    session.add(config)
    await session.commit()
    await session.refresh(config)

    return config


@router.post("/reset-daily-counter")
async def reset_daily_counter(session: AsyncSession = Depends(get_session)):
    """重置每日联系计数"""
    config = await get_or_create_config(session)

    config.today_contacted = 0
    config.updated_at = datetime.now()

    session.add(config)
    await session.commit()

    return {"message": "每日计数已重置", "today_contacted": 0}


@router.post("/increment-daily-counter")
async def increment_daily_counter(session: AsyncSession = Depends(get_session)):
    """增加每日联系计数"""
    config = await get_or_create_config(session)

    # 检查是否需要重置（新的一天）
    if config.last_contact_time:
        last_contact_date = config.last_contact_time.date()
        today_date = date.today()

        if last_contact_date < today_date:
            # 新的一天，重置计数
            config.today_contacted = 0

    config.today_contacted += 1
    config.last_contact_time = datetime.now()
    config.updated_at = datetime.now()

    session.add(config)
    await session.commit()

    return {
        "message": "计数已增加",
        "today_contacted": config.today_contacted,
        "daily_limit": config.daily_limit
    }


@router.get("/check-daily-limit")
async def check_daily_limit(session: AsyncSession = Depends(get_session)):
    """检查是否达到每日限制"""
    config = await get_or_create_config(session)

    # 检查是否需要重置（新的一天）
    if config.last_contact_time:
        last_contact_date = config.last_contact_time.date()
        today_date = date.today()

        if last_contact_date < today_date:
            # 新的一天，重置计数
            config.today_contacted = 0
            session.add(config)
            await session.commit()

    reached_limit = config.today_contacted >= config.daily_limit

    return {
        "reached_limit": reached_limit,
        "today_contacted": config.today_contacted,
        "daily_limit": config.daily_limit,
        "remaining": max(0, config.daily_limit - config.today_contacted)
    }


@router.post("/toggle-auto-mode")
async def toggle_auto_mode(session: AsyncSession = Depends(get_session)):
    """切换自动模式"""
    config = await get_or_create_config(session)

    config.auto_mode_enabled = not config.auto_mode_enabled
    config.updated_at = datetime.now()

    session.add(config)
    await session.commit()

    return {
        "message": f"自动模式已{'启用' if config.auto_mode_enabled else '禁用'}",
        "auto_mode_enabled": config.auto_mode_enabled
    }


@router.post("/toggle-anti-detection")
async def toggle_anti_detection(session: AsyncSession = Depends(get_session)):
    """切换反检测模式"""
    config = await get_or_create_config(session)

    config.anti_detection_enabled = not config.anti_detection_enabled
    config.updated_at = datetime.now()

    session.add(config)
    await session.commit()

    return {
        "message": f"反检测模式已{'启用' if config.anti_detection_enabled else '禁用'}",
        "anti_detection_enabled": config.anti_detection_enabled
    }


@router.post("/toggle-random-delay")
async def toggle_random_delay(session: AsyncSession = Depends(get_session)):
    """切换随机延迟"""
    config = await get_or_create_config(session)

    config.random_delay_enabled = not config.random_delay_enabled
    config.updated_at = datetime.now()

    session.add(config)
    await session.commit()

    return {
        "message": f"随机延迟已{'启用' if config.random_delay_enabled else '禁用'}",
        "random_delay_enabled": config.random_delay_enabled
    }


@router.post("/save-login-info")
async def save_login_info(
    username: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    """保存登录信息"""
    config = await get_or_create_config(session)

    if username:
        config.boss_username = username

    config.boss_session_saved = True
    config.updated_at = datetime.now()

    session.add(config)
    await session.commit()

    return {
        "message": "登录信息已保存",
        "boss_username": config.boss_username,
        "boss_session_saved": config.boss_session_saved
    }


@router.post("/clear-login-info")
async def clear_login_info(session: AsyncSession = Depends(get_session)):
    """清除登录信息"""
    import os

    config = await get_or_create_config(session)

    config.boss_username = None
    config.boss_session_saved = False
    config.updated_at = datetime.now()

    session.add(config)
    await session.commit()

    # 删除保存的登录状态文件
    auth_file = "boss_auth.json"
    if os.path.exists(auth_file):
        os.remove(auth_file)

    return {
        "message": "登录信息已清除",
        "boss_session_saved": False
    }


@router.get("/stats")
async def get_system_stats(session: AsyncSession = Depends(get_session)):
    """获取系统统计信息"""
    from app.models.candidate import Candidate
    from app.models.greeting import GreetingRecord
    from app.models.automation_task import AutomationTask, TaskStatus
    from app.models.greeting_template import GreetingTemplate
    from sqlmodel import func

    config = await get_or_create_config(session)

    # 检查是否需要重置每日计数
    if config.last_contact_time:
        last_contact_date = config.last_contact_time.date()
        today_date = date.today()

        if last_contact_date < today_date:
            config.today_contacted = 0
            session.add(config)
            await session.commit()

    # 候选人统计
    total_candidates_result = await session.execute(
        select(func.count(Candidate.id))
    )
    total_candidates = total_candidates_result.scalar()

    # 今日新增候选人
    today = date.today()
    today_candidates_result = await session.execute(
        select(func.count(Candidate.id)).where(
            func.date(Candidate.created_at) == today
        )
    )
    today_candidates = today_candidates_result.scalar()

    # 问候记录统计
    total_greetings_result = await session.execute(
        select(func.count(GreetingRecord.id))
    )
    total_greetings = total_greetings_result.scalar()

    # 成功的问候
    success_greetings_result = await session.execute(
        select(func.count(GreetingRecord.id)).where(
            GreetingRecord.success == True
        )
    )
    success_greetings = success_greetings_result.scalar()

    # 今日问候
    today_greetings_result = await session.execute(
        select(func.count(GreetingRecord.id)).where(
            func.date(GreetingRecord.sent_at) == today
        )
    )
    today_greetings = today_greetings_result.scalar()

    # 任务统计
    total_tasks_result = await session.execute(
        select(func.count(AutomationTask.id))
    )
    total_tasks = total_tasks_result.scalar()

    running_tasks_result = await session.execute(
        select(func.count(AutomationTask.id)).where(
            AutomationTask.status == TaskStatus.RUNNING
        )
    )
    running_tasks = running_tasks_result.scalar()

    completed_tasks_result = await session.execute(
        select(func.count(AutomationTask.id)).where(
            AutomationTask.status == TaskStatus.COMPLETED
        )
    )
    completed_tasks = completed_tasks_result.scalar()

    # 模板统计
    total_templates_result = await session.execute(
        select(func.count(GreetingTemplate.id))
    )
    total_templates = total_templates_result.scalar()

    active_templates_result = await session.execute(
        select(func.count(GreetingTemplate.id)).where(
            GreetingTemplate.is_active == True
        )
    )
    active_templates = active_templates_result.scalar()

    return {
        "config": {
            "auto_mode_enabled": config.auto_mode_enabled,
            "daily_limit": config.daily_limit,
            "today_contacted": config.today_contacted,
            "remaining_today": max(0, config.daily_limit - config.today_contacted),
            "boss_session_saved": config.boss_session_saved,
            "anti_detection_enabled": config.anti_detection_enabled
        },
        "candidates": {
            "total": total_candidates,
            "today_added": today_candidates
        },
        "greetings": {
            "total": total_greetings,
            "success": success_greetings,
            "success_rate": round(success_greetings / total_greetings * 100, 2) if total_greetings > 0 else 0,
            "today": today_greetings
        },
        "tasks": {
            "total": total_tasks,
            "running": running_tasks,
            "completed": completed_tasks
        },
        "templates": {
            "total": total_templates,
            "active": active_templates
        }
    }
