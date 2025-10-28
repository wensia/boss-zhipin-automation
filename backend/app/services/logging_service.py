"""
日志服务 - 记录系统运行日志到数据库
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import Optional, List
import json
from datetime import datetime

from app.models.log_entry import (
    LogEntry,
    LogEntryCreate,
    LogLevel,
    LogAction,
)


class LoggingService:
    """日志服务类"""

    def __init__(self, session: AsyncSession):
        """初始化日志服务

        Args:
            session: 数据库会话
        """
        self.session = session

    async def log(
        self,
        action: LogAction,
        message: str,
        level: LogLevel = LogLevel.INFO,
        details: Optional[dict] = None,
        task_id: Optional[int] = None,
        task_name: Optional[str] = None,
        user_id: Optional[str] = None,
        user_name: Optional[str] = None,
    ) -> LogEntry:
        """记录日志

        Args:
            action: 操作类型
            message: 日志消息
            level: 日志级别（默认INFO）
            details: 详细信息字典
            task_id: 关联的任务ID
            task_name: 任务名称
            user_id: 用户ID
            user_name: 用户名

        Returns:
            创建的日志条目
        """
        # 将details字典转换为JSON字符串
        details_json = json.dumps(details, ensure_ascii=False) if details else None

        # 创建日志条目
        log_entry = LogEntry(
            level=level,
            action=action,
            message=message,
            details=details_json,
            task_id=task_id,
            task_name=task_name,
            user_id=user_id,
            user_name=user_name,
        )

        # 保存到数据库
        self.session.add(log_entry)
        await self.session.commit()
        await self.session.refresh(log_entry)

        return log_entry

    async def get_logs(
        self,
        limit: int = 100,
        offset: int = 0,
        level: Optional[LogLevel] = None,
        action: Optional[LogAction] = None,
        task_id: Optional[int] = None,
    ) -> tuple[List[LogEntry], int]:
        """获取日志列表

        Args:
            limit: 每页数量
            offset: 偏移量
            level: 筛选日志级别
            action: 筛选操作类型
            task_id: 筛选任务ID

        Returns:
            (日志列表, 总数)
        """
        # 构建查询
        query = select(LogEntry).order_by(LogEntry.created_at.desc())

        # 添加筛选条件
        if level:
            query = query.where(LogEntry.level == level)
        if action:
            query = query.where(LogEntry.action == action)
        if task_id:
            query = query.where(LogEntry.task_id == task_id)

        # 获取总数
        count_query = select(LogEntry)
        if level:
            count_query = count_query.where(LogEntry.level == level)
        if action:
            count_query = count_query.where(LogEntry.action == action)
        if task_id:
            count_query = count_query.where(LogEntry.task_id == task_id)

        result = await self.session.execute(count_query)
        total = len(result.all())

        # 添加分页
        query = query.limit(limit).offset(offset)

        # 执行查询
        result = await self.session.execute(query)
        logs = result.scalars().all()

        return list(logs), total

    async def clear_old_logs(self, days: int = 30) -> int:
        """清理旧日志

        Args:
            days: 保留多少天的日志（默认30天）

        Returns:
            删除的日志数量
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days)

        # 查询要删除的日志
        query = select(LogEntry).where(LogEntry.created_at < cutoff_date)
        result = await self.session.execute(query)
        logs_to_delete = result.scalars().all()

        # 删除日志
        for log in logs_to_delete:
            await self.session.delete(log)

        await self.session.commit()

        return len(logs_to_delete)
