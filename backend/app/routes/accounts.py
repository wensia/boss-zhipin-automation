"""
用户账号管理路由
"""
import json
import os
import httpx
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.models.user_account import UserAccount, UserAccountCreate, UserAccountRead, UserAccountUpdate
from app.models.system_config import SystemConfig
from app.services.boss_automation import BossAutomation

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.get("/", response_model=List[UserAccountRead])
async def list_accounts(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """获取所有账号列表"""
    statement = select(UserAccount).offset(skip).limit(limit).order_by(UserAccount.last_login_at.desc())
    result = await session.execute(statement)
    accounts = result.scalars().all()
    return accounts


@router.get("/current", response_model=Optional[UserAccountRead])
async def get_current_account(
    session: Session = Depends(get_session)
):
    """获取当前激活的账号"""
    # 获取系统配置
    statement = select(SystemConfig)
    result = await session.execute(statement)
    config = result.scalars().first()

    if not config or not config.current_account_id:
        return None

    # 获取当前账号
    account = await session.get(UserAccount, config.current_account_id)
    if not account:
        return None

    return account


@router.get("/by-comid/{com_id}", response_model=UserAccountRead)
async def get_account_by_comid(
    com_id: int,
    session: Session = Depends(get_session)
):
    """通过com_id获取账号"""
    statement = select(UserAccount).where(UserAccount.com_id == com_id)
    result = await session.execute(statement)
    account = result.scalars().first()
    if not account:
        raise HTTPException(status_code=404, detail="账号不存在")
    return account


@router.get("/{account_id}", response_model=UserAccountRead)
async def get_account(
    account_id: int,
    session: Session = Depends(get_session)
):
    """通过account_id获取账号"""
    account = await session.get(UserAccount, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="账号不存在")
    return account


@router.post("/", response_model=UserAccountRead)
async def create_account(
    account_data: UserAccountCreate,
    session: Session = Depends(get_session)
):
    """创建新账号"""
    # 检查com_id是否已存在
    statement = select(UserAccount).where(UserAccount.com_id == account_data.com_id)
    result = await session.execute(statement)
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="该账号已存在")

    account = UserAccount.model_validate(account_data)
    session.add(account)
    await session.commit()
    await session.refresh(account)
    return account


@router.put("/{account_id}", response_model=UserAccountRead)
async def update_account(
    account_id: int,
    account_update: UserAccountUpdate,
    session: Session = Depends(get_session)
):
    """更新账号信息"""
    account = await session.get(UserAccount, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="账号不存在")

    update_data = account_update.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now()

    for key, value in update_data.items():
        setattr(account, key, value)

    session.add(account)
    await session.commit()
    await session.refresh(account)
    return account


@router.delete("/{account_id}")
async def delete_account(
    account_id: int,
    session: Session = Depends(get_session)
):
    """删除账号"""
    account = await session.get(UserAccount, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="账号不存在")

    await session.delete(account)
    await session.commit()
    return {"message": "账号已删除"}


@router.post("/save-from-api")
async def save_account_from_api(
    api_response: dict,
    session: Session = Depends(get_session)
):
    """
    从Boss直聘API响应保存/更新账号信息

    接收API响应数据，自动提取并保存用户信息
    """
    try:
        zp_data = api_response.get("zpData", {})
        base_info = zp_data.get("baseInfo", {})
        contact_info = zp_data.get("contactInfo", {})
        brand = zp_data.get("brand", {})

        com_id = base_info.get("comId")
        if not com_id:
            raise HTTPException(status_code=400, detail="缺少comId")

        # 检查账号是否已存在
        statement = select(UserAccount).where(UserAccount.com_id == com_id)
        result = await session.execute(statement)
        existing_account = result.scalars().first()

        account_data = {
            "com_id": com_id,
            "name": base_info.get("name", ""),
            "show_name": base_info.get("showName", ""),
            "gender": base_info.get("gender", 0),
            "avatar": base_info.get("avatar", ""),
            "title": base_info.get("title", ""),
            "company_name": brand.get("companyFullName", ""),
            "company_short_name": brand.get("name", ""),
            "brand_id": brand.get("brandId", 0),
            "encrypt_brand_id": brand.get("encryptBrandId", ""),
            "company_logo": brand.get("logo", ""),
            "industry": brand.get("industry", ""),
            "resume_email": contact_info.get("resumeEmail"),
            "weixin": contact_info.get("weixin"),
            "cert": zp_data.get("cert", False),
            "cert_gender": zp_data.get("certGender", 0),
            "is_gold": zp_data.get("isGold", 0),
            "raw_data": json.dumps(api_response, ensure_ascii=False),
            "last_login_at": datetime.now()
        }

        if existing_account:
            # 更新现有账号
            for key, value in account_data.items():
                setattr(existing_account, key, value)
            existing_account.updated_at = datetime.now()
            session.add(existing_account)
            await session.commit()
            await session.refresh(existing_account)
            return {"message": "账号信息已更新", "account": existing_account}
        else:
            # 创建新账号
            new_account = UserAccount(**account_data)
            session.add(new_account)
            await session.commit()
            await session.refresh(new_account)
            return {"message": "账号已保存", "account": new_account}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存账号失败: {str(e)}")


@router.post("/{account_id}/set-active", response_model=UserAccountRead)
async def set_active_account(
    account_id: int,
    session: Session = Depends(get_session)
):
    """设置当前激活账号"""
    # 检查账号是否存在
    account = await session.get(UserAccount, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="账号不存在")

    # 获取或创建系统配置
    statement = select(SystemConfig)
    result = await session.execute(statement)
    config = result.scalars().first()

    if not config:
        # 创建默认配置
        config = SystemConfig()
        session.add(config)

    # 更新当前账号ID
    config.current_account_id = account_id
    config.updated_at = datetime.now()

    await session.commit()
    await session.refresh(account)

    return account


@router.get("/{account_id}/verify-login")
async def verify_account_login(
    account_id: int,
    session: Session = Depends(get_session)
):
    """验证账号登录状态"""
    # 获取账号信息
    account = await session.get(UserAccount, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="账号不存在")

    # 检查登录状态文件是否存在
    auth_file = BossAutomation.get_auth_file_path(account.com_id)
    file_exists = os.path.exists(auth_file)

    if not file_exists:
        return {
            "valid": False,
            "message": "未保存登录状态",
            "needs_login": True
        }

    # 返回文件存在的信息（实际验证需要浏览器）
    return {
        "valid": True,
        "message": "已保存登录状态",
        "needs_login": False,
        "auth_file": auth_file
    }


@router.get("/{account_id}/recruit-data")
async def get_recruit_data(
    account_id: int,
    session: Session = Depends(get_session)
):
    """获取账号的招聘数据中心数据"""
    # 获取账号信息
    account = await session.get(UserAccount, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="账号不存在")

    # 获取认证文件路径
    auth_file = BossAutomation.get_auth_file_path(account.com_id)
    if not os.path.exists(auth_file):
        raise HTTPException(status_code=400, detail="账号未登录，请先登录")

    # 读取认证信息
    try:
        with open(auth_file, 'r', encoding='utf-8') as f:
            auth_data = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取认证信息失败: {str(e)}")

    # 提取cookies并转换为HTTP请求格式
    cookies_dict = {}
    for cookie in auth_data.get('cookies', []):
        cookies_dict[cookie['name']] = cookie['value']

    # 构建请求头
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'priority': 'u=1, i',
        'referer': 'https://www.zhipin.com/web/frame/report/data-center',
        'sec-ch-ua': '"Not=A?Brand";v="24", "Chromium";v="140"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    # 添加zp_token (从cookies中获取bst的值)
    if 'bst' in cookies_dict:
        headers['zp_token'] = cookies_dict['bst']

    # 调用Boss直聘API
    api_url = 'https://www.zhipin.com/wapi/zpboss/h5/weeklyReportV3/recruitDataCenter/get.json'
    params = {
        'jobId': '0',
        'platform': '1',
        'date': ''
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                api_url,
                params=params,
                headers=headers,
                cookies=cookies_dict,
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            return data
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"API请求失败: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取招聘数据失败: {str(e)}")
