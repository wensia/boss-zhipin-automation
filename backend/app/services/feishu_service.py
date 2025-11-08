"""
飞书多维表格服务
"""
import time
from typing import Optional, Dict, List, Any
import httpx


class FeishuBitableService:
    """飞书多维表格服务类"""

    def __init__(self, app_id: str, app_secret: str):
        """
        初始化飞书多维表格服务

        Args:
            app_id: 飞书应用 App ID
            app_secret: 飞书应用 App Secret
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = "https://open.feishu.cn/open-apis"
        self.token: Optional[str] = None
        self.token_expires_at: float = 0

    async def get_tenant_access_token(self) -> str:
        """
        获取租户访问令牌（tenant_access_token）

        Returns:
            访问令牌
        """
        # 检查令牌是否过期（提前5分钟刷新）
        if self.token and time.time() < self.token_expires_at - 300:
            return self.token

        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10.0
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    self.token = result['tenant_access_token']
                    # 令牌有效期为2小时（7200秒）
                    self.token_expires_at = time.time() + result.get('expire', 7200)
                    return self.token
                else:
                    raise Exception(f"获取令牌失败: {result.get('msg')}")
            else:
                raise Exception(f"请求失败: HTTP {response.status_code}")

    async def list_fields(self, app_token: str, table_id: str) -> List[Dict[str, Any]]:
        """
        获取数据表的字段列表

        Args:
            app_token: 多维表格 App Token
            table_id: 数据表 Table ID

        Returns:
            字段列表
        """
        token = await self.get_tenant_access_token()
        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/fields"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                timeout=10.0
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    return result.get('data', {}).get('items', [])
                else:
                    raise Exception(f"获取字段失败: {result.get('msg')}")
            else:
                raise Exception(f"请求失败: HTTP {response.status_code}")

    async def create_field(
        self,
        app_token: str,
        table_id: str,
        field_name: str,
        field_type: int,
        property: Optional[Dict] = None
    ) -> str:
        """
        创建字段

        Args:
            app_token: 多维表格 App Token
            table_id: 数据表 Table ID
            field_name: 字段名称
            field_type: 字段类型（1=文本, 2=数字, 3=单选, 4=多选, 5=日期, 15=URL等）
            property: 字段属性（可选）

        Returns:
            字段 ID
        """
        token = await self.get_tenant_access_token()
        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/fields"

        payload = {
            "field_name": field_name,
            "type": field_type
        }

        if property:
            payload["property"] = property

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                timeout=10.0
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    return result['data']['field']['field_id']
                else:
                    raise Exception(f"创建字段失败: {result.get('msg')}")
            else:
                raise Exception(f"请求失败: HTTP {response.status_code}")

    async def update_field(
        self,
        app_token: str,
        table_id: str,
        field_id: str,
        field_name: Optional[str] = None,
        property: Optional[Dict] = None
    ) -> bool:
        """
        更新字段

        Args:
            app_token: 多维表格 App Token
            table_id: 数据表 Table ID
            field_id: 字段 ID
            field_name: 新的字段名称（可选）
            property: 新的字段属性（可选）

        Returns:
            是否成功
        """
        token = await self.get_tenant_access_token()
        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/fields/{field_id}"

        payload = {}
        if field_name:
            payload["field_name"] = field_name
        if property:
            payload["property"] = property

        if not payload:
            raise ValueError("至少需要提供 field_name 或 property 参数")

        async with httpx.AsyncClient() as client:
            response = await client.put(
                url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                timeout=10.0
            )

            if response.status_code == 200:
                result = response.json()
                return result.get('code') == 0
            else:
                raise Exception(f"请求失败: HTTP {response.status_code}")

    async def delete_field(
        self,
        app_token: str,
        table_id: str,
        field_id: str
    ) -> bool:
        """
        删除字段

        Args:
            app_token: 多维表格 App Token
            table_id: 数据表 Table ID
            field_id: 字段 ID

        Returns:
            是否成功
        """
        token = await self.get_tenant_access_token()
        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/fields/{field_id}"

        async with httpx.AsyncClient() as client:
            response = await client.delete(
                url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                timeout=10.0
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    return True
                else:
                    raise Exception(f"删除字段失败: {result.get('msg')}")
            else:
                raise Exception(f"请求失败: HTTP {response.status_code}")

    async def insert_record(
        self,
        app_token: str,
        table_id: str,
        fields: Dict[str, Any]
    ) -> str:
        """
        插入记录

        Args:
            app_token: 多维表格 App Token
            table_id: 数据表 Table ID
            fields: 字段数据

        Returns:
            记录 ID
        """
        token = await self.get_tenant_access_token()
        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records"

        payload = {
            "fields": fields
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                timeout=10.0
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    return result['data']['record']['record_id']
                else:
                    raise Exception(f"插入记录失败: {result.get('msg')}")
            else:
                raise Exception(f"请求失败: HTTP {response.status_code}")

    async def batch_insert_records(
        self,
        app_token: str,
        table_id: str,
        records: List[Dict[str, Any]]
    ) -> List[str]:
        """
        批量插入记录

        Args:
            app_token: 多维表格 App Token
            table_id: 数据表 Table ID
            records: 记录列表，每个记录是 {"fields": {...}}

        Returns:
            记录 ID 列表
        """
        token = await self.get_tenant_access_token()
        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create"

        payload = {
            "records": records
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                timeout=30.0  # 批量操作可能需要更长时间
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    return [r['record_id'] for r in result['data']['records']]
                else:
                    raise Exception(f"批量插入记录失败: {result.get('msg')}")
            else:
                raise Exception(f"请求失败: HTTP {response.status_code}")

    async def list_records(
        self,
        app_token: str,
        table_id: str,
        page_size: int = 100,
        page_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取记录列表

        Args:
            app_token: 多维表格 App Token
            table_id: 数据表 Table ID
            page_size: 每页记录数（最大500）
            page_token: 分页标记（可选）

        Returns:
            包含记录列表和分页信息的字典
        """
        token = await self.get_tenant_access_token()
        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records"

        params = {
            "page_size": min(page_size, 500)
        }
        if page_token:
            params["page_token"] = page_token

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                timeout=10.0
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    return result.get('data', {})
                else:
                    raise Exception(f"获取记录失败: {result.get('msg')}")
            else:
                raise Exception(f"请求失败: HTTP {response.status_code}")

    async def update_record(
        self,
        app_token: str,
        table_id: str,
        record_id: str,
        fields: Dict[str, Any]
    ) -> bool:
        """
        更新记录

        Args:
            app_token: 多维表格 App Token
            table_id: 数据表 Table ID
            record_id: 记录 ID
            fields: 要更新的字段数据

        Returns:
            是否成功
        """
        token = await self.get_tenant_access_token()
        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"

        payload = {
            "fields": fields
        }

        async with httpx.AsyncClient() as client:
            response = await client.put(
                url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                timeout=10.0
            )

            if response.status_code == 200:
                result = response.json()
                return result.get('code') == 0
            else:
                raise Exception(f"请求失败: HTTP {response.status_code}")

    async def delete_record(
        self,
        app_token: str,
        table_id: str,
        record_id: str
    ) -> bool:
        """
        删除记录

        Args:
            app_token: 多维表格 App Token
            table_id: 数据表 Table ID
            record_id: 记录 ID

        Returns:
            是否成功
        """
        token = await self.get_tenant_access_token()
        url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"

        async with httpx.AsyncClient() as client:
            response = await client.delete(
                url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                timeout=10.0
            )

            if response.status_code == 200:
                result = response.json()
                return result.get('code') == 0
            else:
                raise Exception(f"请求失败: HTTP {response.status_code}")

    async def create_candidate_table_structure(
        self,
        app_token: str,
        table_id: str
    ) -> Dict[str, str]:
        """
        为候选人表格创建字段结构

        Args:
            app_token: 多维表格 App Token
            table_id: 数据表 Table ID

        Returns:
            字段名称到字段ID的映射
        """
        # 定义候选人表格的所有字段
        fields_definition = [
            {"name": "Boss直聘ID", "type": 1},  # 文本
            {"name": "姓名", "type": 1},
            {"name": "头像", "type": 15},  # URL
            {"name": "当前职位", "type": 1},
            {"name": "当前公司", "type": 1},
            {"name": "工作年限", "type": 1},
            {
                "name": "学历",
                "type": 3,  # 单选
                "property": {
                    "options": [
                        {"name": "高中及以下"},
                        {"name": "大专"},
                        {"name": "本科"},
                        {"name": "硕士"},
                        {"name": "博士"}
                    ]
                }
            },
            {"name": "期望职位", "type": 1},
            {"name": "期望薪资", "type": 1},
            {"name": "期望地点", "type": 1},
            {
                "name": "状态",
                "type": 3,  # 单选
                "property": {
                    "options": [
                        {"name": "新发现"},
                        {"name": "已沟通"},
                        {"name": "已回复"},
                        {"name": "有意向"},
                        {"name": "已拒绝"},
                        {"name": "已归档"}
                    ]
                }
            },
            {"name": "最近活跃时间", "type": 5},  # 日期
            {"name": "最后沟通时间", "type": 5},
            {"name": "个人主页URL", "type": 15},  # URL
            {"name": "备注", "type": 2},  # 多行文本
        ]

        field_ids = {}
        for field_def in fields_definition:
            try:
                field_id = await self.create_field(
                    app_token,
                    table_id,
                    field_def["name"],
                    field_def["type"],
                    field_def.get("property")
                )
                field_ids[field_def["name"]] = field_id
                print(f"✓ 创建字段: {field_def['name']}")
            except Exception as e:
                print(f"✗ 创建字段失败 {field_def['name']}: {e}")

        return field_ids

    async def insert_candidate(
        self,
        app_token: str,
        table_id: str,
        candidate_data: Dict[str, Any]
    ) -> str:
        """
        插入候选人记录

        Args:
            app_token: 多维表格 App Token
            table_id: 数据表 Table ID
            candidate_data: 候选人数据

        Returns:
            记录 ID
        """
        # 构建字段映射
        fields = {
            "Boss直聘ID": candidate_data.get("boss_id"),
            "姓名": candidate_data.get("name"),
            "头像": candidate_data.get("avatar"),
            "当前职位": candidate_data.get("position"),
            "当前公司": candidate_data.get("company"),
            "工作年限": candidate_data.get("work_experience"),
            "学历": candidate_data.get("education"),
            "期望职位": candidate_data.get("expected_position"),
            "期望薪资": candidate_data.get("expected_salary"),
            "期望地点": candidate_data.get("expected_location"),
            "状态": candidate_data.get("status", "新发现"),
            "个人主页URL": candidate_data.get("profile_url"),
            "备注": candidate_data.get("notes"),
        }

        # 处理时间字段（转为毫秒时间戳）
        if candidate_data.get("active_time"):
            fields["最近活跃时间"] = int(candidate_data["active_time"].timestamp() * 1000)
        if candidate_data.get("last_contacted_at"):
            fields["最后沟通时间"] = int(candidate_data["last_contacted_at"].timestamp() * 1000)

        # 过滤掉 None 值
        fields = {k: v for k, v in fields.items() if v is not None}

        return await self.insert_record(app_token, table_id, fields)

    async def create_greeting_record_table_structure(
        self,
        app_token: str,
        table_id: str
    ) -> Dict[str, str]:
        """
        为打招呼记录表格创建字段结构

        Args:
            app_token: 多维表格 App Token
            table_id: 数据表 Table ID

        Returns:
            字段名称到字段ID的映射
        """
        # 定义打招呼记录表格的所有字段
        fields_definition = [
            # 候选人基本信息
            {"name": "Boss直聘ID", "type": 1},  # 文本
            {"name": "候选人姓名", "type": 1},
            {"name": "头像", "type": 15},  # URL
            {"name": "当前职位", "type": 1},
            {"name": "当前公司", "type": 1},
            {"name": "工作年限", "type": 1},
            {"name": "学历", "type": 1},

            # 打招呼信息
            {"name": "打招呼消息", "type": 2},  # 多行文本
            {"name": "使用模板", "type": 1},
            {"name": "发送时间", "type": 5},  # 日期

            # 执行结果
            {
                "name": "执行状态",
                "type": 3,  # 单选
                "property": {
                    "options": [
                        {"name": "成功"},
                        {"name": "失败"},
                        {"name": "跳过"}
                    ]
                }
            },
            {"name": "错误信息", "type": 2},  # 多行文本

            # 任务信息
            {"name": "任务ID", "type": 2},  # 数字
            {"name": "任务名称", "type": 1},

            # 候选人扩展信息
            {"name": "期望职位", "type": 1},
            {"name": "期望薪资", "type": 1},
            {"name": "期望地点", "type": 1},
            {"name": "个人主页URL", "type": 15},  # URL
            {"name": "最近活跃时间", "type": 5},  # 日期
            {"name": "备注", "type": 2},  # 多行文本
        ]

        field_ids = {}
        for field_def in fields_definition:
            try:
                field_id = await self.create_field(
                    app_token,
                    table_id,
                    field_def["name"],
                    field_def["type"],
                    field_def.get("property")
                )
                field_ids[field_def["name"]] = field_id
                print(f"✓ 创建字段: {field_def['name']}")
            except Exception as e:
                print(f"✗ 创建字段失败 {field_def['name']}: {e}")

        return field_ids

    async def insert_greeting_record(
        self,
        app_token: str,
        table_id: str,
        greeting_data: Dict[str, Any]
    ) -> str:
        """
        插入打招呼记录

        Args:
            app_token: 多维表格 App Token
            table_id: 数据表 Table ID
            greeting_data: 打招呼记录数据

        Returns:
            记录 ID
        """
        # 构建字段映射
        fields = {
            # 候选人基本信息
            "Boss直聘ID": greeting_data.get("boss_id"),
            "候选人姓名": greeting_data.get("candidate_name"),
            "头像": greeting_data.get("avatar"),
            "当前职位": greeting_data.get("position"),
            "当前公司": greeting_data.get("company"),
            "工作年限": greeting_data.get("work_experience"),
            "学历": greeting_data.get("education"),

            # 打招呼信息
            "打招呼消息": greeting_data.get("message"),
            "使用模板": greeting_data.get("template_name"),
            "执行状态": "成功" if greeting_data.get("success") else "失败",
            "错误信息": greeting_data.get("error_message"),

            # 任务信息
            "任务ID": str(greeting_data.get("task_id")) if greeting_data.get("task_id") else None,
            "任务名称": greeting_data.get("task_name"),

            # 候选人扩展信息
            "期望职位": greeting_data.get("expected_position"),
            "期望薪资": greeting_data.get("expected_salary"),
            "期望地点": greeting_data.get("expected_location"),
            "个人主页URL": greeting_data.get("profile_url"),
            "备注": greeting_data.get("notes"),
        }

        # 处理时间字段（转为毫秒时间戳）
        if greeting_data.get("sent_at"):
            fields["发送时间"] = int(greeting_data["sent_at"].timestamp() * 1000)
        if greeting_data.get("active_time"):
            fields["最近活跃时间"] = int(greeting_data["active_time"].timestamp() * 1000)

        # 过滤掉 None 值
        fields = {k: v for k, v in fields.items() if v is not None}

        return await self.insert_record(app_token, table_id, fields)

    async def sync_greeting_record_fields(
        self,
        app_token: str,
        table_id: str
    ) -> Dict[str, Any]:
        """
        同步打招呼记录表字段（只创建缺失的字段，不删除现有字段）

        Args:
            app_token: 多维表格 App Token
            table_id: 数据表 Table ID

        Returns:
            包含操作结果的字典：{"existing": [], "created": [], "failed": []}
        """
        # 获取现有字段
        existing_fields = await self.list_fields(app_token, table_id)
        existing_field_names = {field.get("field_name") for field in existing_fields}

        # 定义需要的字段
        required_fields = [
            {"name": "Boss直聘ID", "type": 1},
            {"name": "候选人姓名", "type": 1},
            {"name": "头像", "type": 15},
            {"name": "当前职位", "type": 1},
            {"name": "当前公司", "type": 1},
            {"name": "工作年限", "type": 1},
            {"name": "学历", "type": 1},
            {"name": "打招呼消息", "type": 2},
            {"name": "使用模板", "type": 1},
            {"name": "发送时间", "type": 5},
            {
                "name": "执行状态",
                "type": 3,
                "property": {
                    "options": [
                        {"name": "成功"},
                        {"name": "失败"},
                        {"name": "跳过"}
                    ]
                }
            },
            {"name": "错误信息", "type": 2},
            {"name": "任务ID", "type": 2},
            {"name": "任务名称", "type": 1},
            {"name": "期望职位", "type": 1},
            {"name": "期望薪资", "type": 1},
            {"name": "期望地点", "type": 1},
            {"name": "个人主页URL", "type": 15},
            {"name": "最近活跃时间", "type": 5},
            {"name": "备注", "type": 2},
        ]

        result = {
            "existing": [],
            "created": [],
            "failed": []
        }

        # 检查并创建缺失的字段
        for field_def in required_fields:
            field_name = field_def["name"]

            if field_name in existing_field_names:
                result["existing"].append(field_name)
                print(f"⏭️  字段已存在: {field_name}")
            else:
                try:
                    field_id = await self.create_field(
                        app_token,
                        table_id,
                        field_name,
                        field_def["type"],
                        field_def.get("property")
                    )
                    result["created"].append({"name": field_name, "id": field_id})
                    print(f"✓ 创建字段: {field_name}")
                except Exception as e:
                    result["failed"].append({"name": field_name, "error": str(e)})
                    print(f"✗ 创建字段失败 {field_name}: {e}")

        return result
