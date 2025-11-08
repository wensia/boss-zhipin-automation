"""
日志相关 API 路由
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.database import get_session
from app.services.logging_service import LoggingService
from app.models.log_entry import (
    LogEntry,
    LogEntryRead,
    LogEntryCreate,
    LogLevel,
    LogAction,
)

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("", response_model=dict)
async def get_logs(
    limit: int = Query(default=100, ge=1, le=500, description="每页数量"),
    offset: int = Query(default=0, ge=0, description="偏移量"),
    level: Optional[LogLevel] = Query(default=None, description="筛选日志级别"),
    action: Optional[LogAction] = Query(default=None, description="筛选操作类型"),
    task_id: Optional[int] = Query(default=None, description="筛选任务ID"),
    session: AsyncSession = Depends(get_session),
):
    """
    获取日志列表（支持分页和筛选）
    """
    logging_service = LoggingService(session)
    logs, total = await logging_service.get_logs(
        limit=limit,
        offset=offset,
        level=level,
        action=action,
        task_id=task_id,
    )

    return {
        "logs": [
            {
                "id": log.id,
                "level": log.level,
                "action": log.action,
                "message": log.message,
                "details": log.details,
                "task_id": log.task_id,
                "task_name": log.task_name,
                "user_id": log.user_id,
                "user_name": log.user_name,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("", response_model=LogEntryRead)
async def create_log(
    log_data: LogEntryCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    创建日志条目
    """
    logging_service = LoggingService(session)
    log_entry = await logging_service.log(
        action=log_data.action,
        message=log_data.message,
        level=log_data.level,
        details=None if not log_data.details else eval(log_data.details),
        task_id=log_data.task_id,
        task_name=log_data.task_name,
        user_id=log_data.user_id,
        user_name=log_data.user_name,
    )
    return log_entry


@router.delete("/old", response_model=dict)
async def clear_old_logs(
    days: int = Query(default=30, ge=1, le=365, description="保留多少天的日志"),
    session: AsyncSession = Depends(get_session),
):
    """
    清理旧日志
    """
    logging_service = LoggingService(session)
    deleted_count = await logging_service.clear_old_logs(days=days)

    return {
        "message": f"已清理 {deleted_count} 条旧日志（{days}天前）",
        "deleted_count": deleted_count,
    }
