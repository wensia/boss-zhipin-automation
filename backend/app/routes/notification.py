"""
通知配置 API 路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime

from app.database import get_session
from app.models.notification_config import (
    NotificationConfig,
    NotificationConfigCreate,
    NotificationConfigUpdate
)

router = APIRouter(prefix="/api/notification", tags=["notification"])


@router.get("/config", response_model=NotificationConfig)
async def get_notification_config(
    session: AsyncSession = Depends(get_session)
):
    """获取通知配置（返回第一条，如果不存在则创建默认配置）"""
    result = await session.execute(
        select(NotificationConfig).limit(1)
    )
    config = result.scalar_one_or_none()

    if not config:
        # 创建默认配置
        config = NotificationConfig(
            dingtalk_enabled=False,
            dingtalk_webhook=None,
            dingtalk_secret=None,
            feishu_enabled=False,
            feishu_webhook=None,
            feishu_secret=None,
            feishu_bitable_enabled=False,
            feishu_app_id=None,
            feishu_app_secret=None,
            feishu_app_token=None,
            feishu_table_id=None,
            notify_on_completion=True,
            notify_on_limit=True,
            notify_on_error=True
        )
        session.add(config)
        await session.commit()
        await session.refresh(config)

    return config


@router.put("/config", response_model=NotificationConfig)
async def update_notification_config(
    config_data: NotificationConfigUpdate,
    session: AsyncSession = Depends(get_session)
):
    """更新通知配置"""
    result = await session.execute(
        select(NotificationConfig).limit(1)
    )
    config = result.scalar_one_or_none()

    if not config:
        # 如果不存在，创建新配置
        config = NotificationConfig()
        session.add(config)

    # 更新字段
    update_data = config_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)

    config.updated_at = datetime.now()

    await session.commit()
    await session.refresh(config)

    return config


@router.post("/test-dingtalk")
async def test_dingtalk_notification(
    session: AsyncSession = Depends(get_session)
):
    """测试钉钉通知"""
    from app.services.notification_service import NotificationService

    # 获取配置
    result = await session.execute(
        select(NotificationConfig).limit(1)
    )
    config = result.scalar_one_or_none()

    if not config or not config.dingtalk_enabled:
        raise HTTPException(status_code=400, detail="钉钉通知未启用")

    if not config.dingtalk_webhook:
        raise HTTPException(status_code=400, detail="钉钉Webhook地址未配置")

    # 发送测试通知
    notification_service = NotificationService(config)
    success = await notification_service.send_test_message()

    if not success:
        raise HTTPException(status_code=500, detail="发送测试消息失败")

    return {"success": True, "message": "测试消息已发送"}


@router.post("/test-feishu")
async def test_feishu_notification(
    session: AsyncSession = Depends(get_session)
):
    """测试飞书通知"""
    from app.services.notification_service import NotificationService

    # 获取配置
    result = await session.execute(
        select(NotificationConfig).limit(1)
    )
    config = result.scalar_one_or_none()

    if not config or not config.feishu_enabled:
        raise HTTPException(status_code=400, detail="飞书通知未启用")

    if not config.feishu_webhook:
        raise HTTPException(status_code=400, detail="飞书Webhook地址未配置")

    # 发送测试通知
    notification_service = NotificationService(config)
    success = await notification_service.send_feishu_test_message()

    if not success:
        raise HTTPException(status_code=500, detail="发送测试消息失败")

    return {"success": True, "message": "飞书测试消息已发送"}


@router.post("/test-feishu-bitable")
async def test_feishu_bitable_connection(
    session: AsyncSession = Depends(get_session)
):
    """测试飞书多维表格连接"""
    # 获取配置
    result = await session.execute(
        select(NotificationConfig).limit(1)
    )
    config = result.scalar_one_or_none()

    if not config or not config.feishu_bitable_enabled:
        raise HTTPException(status_code=400, detail="飞书多维表格同步未启用")

    if not config.feishu_app_id or not config.feishu_app_secret:
        raise HTTPException(status_code=400, detail="飞书应用凭证未配置")

    if not config.feishu_app_token or not config.feishu_table_id:
        raise HTTPException(status_code=400, detail="飞书多维表格信息未配置")

    try:
        from app.services.feishu_service import FeishuBitableService

        # 初始化服务并测试连接
        feishu_service = FeishuBitableService(
            config.feishu_app_id,
            config.feishu_app_secret
        )

        # 测试获取表格字段
        fields = await feishu_service.list_fields(
            config.feishu_app_token,
            config.feishu_table_id
        )

        return {
            "success": True,
            "message": "飞书多维表格连接成功",
            "field_count": len(fields) if fields else 0
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"连接测试失败: {str(e)}"
        )


@router.post("/sync-greeting-fields")
async def sync_greeting_record_fields(
    session: AsyncSession = Depends(get_session)
):
    """同步打招呼记录表的字段结构"""
    # 获取配置
    result = await session.execute(
        select(NotificationConfig).limit(1)
    )
    config = result.scalar_one_or_none()

    if not config or not config.feishu_bitable_enabled:
        raise HTTPException(status_code=400, detail="飞书多维表格同步未启用")

    if not config.feishu_app_id or not config.feishu_app_secret:
        raise HTTPException(status_code=400, detail="飞书应用凭证未配置")

    if not config.feishu_app_token or not config.feishu_table_id:
        raise HTTPException(status_code=400, detail="飞书多维表格信息未配置")

    try:
        from app.services.feishu_service import FeishuBitableService

        # 初始化服务
        feishu_service = FeishuBitableService(
            config.feishu_app_id,
            config.feishu_app_secret
        )

        # 同步字段结构
        sync_result = await feishu_service.sync_greeting_record_fields(
            config.feishu_app_token,
            config.feishu_table_id
        )

        return {
            "success": True,
            "message": "字段同步完成",
            "existing_count": len(sync_result["existing"]),
            "created_count": len(sync_result["created"]),
            "failed_count": len(sync_result["failed"]),
            "details": sync_result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"字段同步失败: {str(e)}"
        )
