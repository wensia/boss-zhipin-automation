"""
打招呼自动化API路由
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from app.services.greeting_service import greeting_manager

# 导入全局自动化服务
import sys
sys.path.append('..')
from app.routes.automation import get_automation_service

router = APIRouter(prefix="/api/greeting", tags=["greeting"])


class StartGreetingRequest(BaseModel):
    """开始打招呼请求"""
    target_count: int = Field(..., ge=1, le=300, description="打招呼数量（1-300）")
    expected_positions: List[str] = Field(default=[], description="期望职位关键词列表（包含匹配）")


class GreetingStatusResponse(BaseModel):
    """打招呼状态响应"""
    status: str
    target_count: int
    current_index: int
    success_count: int
    failed_count: int
    skipped_count: int = 0
    progress: float
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    elapsed_time: Optional[float] = None
    error_message: Optional[str] = None


class LogEntry(BaseModel):
    """日志条目"""
    timestamp: str
    level: str
    message: str


class GreetingLogsResponse(BaseModel):
    """日志响应"""
    logs: List[LogEntry]


@router.post("/start", summary="开始打招呼任务")
async def start_greeting(request: StartGreetingRequest):
    """
    启动自动打招呼任务

    - **target_count**: 打招呼数量（1-300）
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"收到打招呼请求: target_count={request.target_count}, expected_positions={request.expected_positions}")

    try:
        # 检查是否已有任务在运行
        if greeting_manager.status == "running":
            # 检查任务是否超时（超过30分钟自动重置）
            if greeting_manager.is_stale(timeout_minutes=30):
                logger.warning("⚠️ 检测到超时任务（超过30分钟），自动重置...")
                greeting_manager.reset()
                logger.info("✅ 超时任务已自动重置，继续启动新任务")
            else:
                raise HTTPException(status_code=400, detail="已有任务正在运行，请等待完成或停止当前任务")

        # 获取全局自动化服务（复用已打开的浏览器）
        automation = await get_automation_service()

        if not automation.is_logged_in:
            raise HTTPException(status_code=401, detail="未登录，请先在向导中完成登录")

        if not automation.page:
            raise HTTPException(status_code=400, detail="浏览器未初始化，请先在向导中初始化浏览器")

        # 启动任务（传入已有的自动化服务和期望职位列表）
        await greeting_manager.start_greeting_task(
            target_count=request.target_count,
            automation_service=automation,
            expected_positions=request.expected_positions
        )

        return {
            "success": True,
            "message": f"已启动打招呼任务，目标数量: {request.target_count}",
            "task_id": "greeting_task_1"  # 简化版，实际可以生成唯一ID
        }

    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动任务失败: {str(e)}")


@router.get("/status", response_model=GreetingStatusResponse, summary="获取任务状态")
async def get_greeting_status():
    """
    获取当前打招呼任务的状态和进度

    返回信息包括：
    - status: 任务状态（idle, running, completed, error）
    - progress: 完成进度（百分比）
    - success_count: 成功数量
    - failed_count: 失败数量
    """
    status = greeting_manager.get_status()
    return status


@router.get("/logs", response_model=GreetingLogsResponse, summary="获取任务日志")
async def get_greeting_logs(last_n: int = 50):
    """
    获取最近的任务日志

    - **last_n**: 获取最近N条日志（默认50）
    """
    logs = greeting_manager.get_logs(last_n=last_n)
    return {"logs": logs}


@router.post("/stop", summary="停止任务")
async def stop_greeting():
    """
    停止当前正在运行的打招呼任务
    """
    try:
        if greeting_manager.status != "running":
            raise HTTPException(status_code=400, detail="没有正在运行的任务")

        await greeting_manager.stop_task()

        return {
            "success": True,
            "message": "任务已停止"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"停止任务失败: {str(e)}")


@router.post("/reset", summary="重置任务状态")
async def reset_greeting():
    """
    重置任务状态（清除历史记录和日志）
    """
    try:
        if greeting_manager.status == "running":
            raise HTTPException(status_code=400, detail="任务正在运行，请先停止")

        greeting_manager.reset()

        return {
            "success": True,
            "message": "任务状态已重置"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重置失败: {str(e)}")


@router.post("/force-reset", summary="强制重置任务状态")
async def force_reset_greeting():
    """
    强制重置任务状态，即使任务正在运行也会强制停止并重置

    用于处理僵尸任务状态（任务卡在running但实际已停止）
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        logger.warning(f"⚠️ 执行强制重置，当前状态: {greeting_manager.status}")

        # 强制重置（会取消运行中的任务）
        greeting_manager.reset()

        logger.info("✅ 强制重置完成")

        return {
            "success": True,
            "message": "任务状态已强制重置"
        }
    except Exception as e:
        logger.error(f"❌ 强制重置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"强制重置失败: {str(e)}")
