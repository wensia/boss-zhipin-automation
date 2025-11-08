from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator

# SQLite数据库配置
DATABASE_URL = "sqlite+aiosqlite:///./database.db"

# 创建异步引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # 开发时启用SQL日志
    future=True,
    connect_args={"check_same_thread": False}  # SQLite需要此配置
)

# 创建异步会话工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """初始化数据库,创建所有表"""
    # 导入所有模型以确保表被创建
    from app.models.candidate import Candidate
    from app.models.greeting import GreetingRecord
    from app.models.automation_task import AutomationTask
    from app.models.greeting_template import GreetingTemplate
    from app.models.system_config import SystemConfig
    from app.models.log_entry import LogEntry
    from app.models.user_account import UserAccount
    from app.models.notification_config import NotificationConfig
    from app.models.filters import FilterOptions
    from app.models.automation_template import AutomationTemplate

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话的依赖注入函数"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
