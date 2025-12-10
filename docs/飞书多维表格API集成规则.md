# 飞书多维表格API集成规则

本文档记录飞书多维表格API的使用规范，用于后续实现将已打招呼的候选人信息写入飞书多维表格功能。

## 一、API概述

飞书多维表格（Bitable）是飞书开放平台提供的数据管理服务，支持通过API进行数据的增删改查操作。

**官方文档入口**：https://open.feishu.cn/document/server-docs/docs/bitable-v1/bitable-overview

---

## 二、开发前准备

### 2.1 创建飞书应用

1. 登录 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 获取 `App ID` 和 `App Secret`

### 2.2 申请权限

在应用的"权限管理" → "API权限"中申请以下权限：

| 权限名称 | 权限标识 | 说明 |
|---------|---------|------|
| 查看、评论、编辑和管理多维表格 | `bitable:app` | 多维表格读写权限 |
| 查看、评论、编辑和管理云空间中所有文件 | `drive:drive` | 云空间文件权限 |

### 2.3 启用机器人能力（可选）

若需通过机器人操作用户创建的多维表格：
1. 在应用后台启用"机器人"能力
2. 创建群组，将应用添加为群机器人
3. 将目标文件夹分享给该群组

### 2.4 获取必要参数

| 参数 | 说明 | 获取方式 |
|------|------|---------|
| `app_token` | 多维表格唯一标识 | 从多维表格URL中获取 |
| `table_id` | 数据表ID | 从数据表URL或API获取 |
| `view_id` | 视图ID | 可选，从视图URL或API获取 |

**URL示例**：
```
https://xxx.feishu.cn/base/{app_token}?table={table_id}&view={view_id}
```

---

## 三、认证鉴权

### 3.1 获取 Access Token

**接口地址**：`POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal`

**请求体**：
```json
{
  "app_id": "cli_xxx",
  "app_secret": "xxx"
}
```

**响应示例**：
```json
{
  "code": 0,
  "msg": "success",
  "tenant_access_token": "t-xxx",
  "expire": 7200
}
```

### 3.2 请求头设置

```python
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}
```

---

## 四、核心API接口

### 4.1 记录操作

#### 新增单条记录

**接口**：`POST /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records`

**请求体**：
```json
{
  "fields": {
    "姓名": "张三",
    "职位": "前端工程师",
    "公司": "xxx科技",
    "打招呼时间": 1699200000000,
    "状态": "已发送"
  }
}
```

#### 批量新增记录

**接口**：`POST /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create`

**请求体**：
```json
{
  "records": [
    {
      "fields": {
        "姓名": "张三",
        "职位": "前端工程师"
      }
    },
    {
      "fields": {
        "姓名": "李四",
        "职位": "后端工程师"
      }
    }
  ]
}
```

#### 更新记录

**接口**：`PUT /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}`

**请求体**：
```json
{
  "fields": {
    "状态": "已回复"
  }
}
```

#### 批量更新记录

**接口**：`POST /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_update`

**请求体**：
```json
{
  "records": [
    {
      "record_id": "recxxx",
      "fields": {
        "状态": "已回复"
      }
    }
  ]
}
```

#### 查询记录列表

**接口**：`GET /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records`

**查询参数**：
- `page_size`: 分页大小，最大500
- `page_token`: 分页标记
- `filter`: 筛选条件
- `sort`: 排序规则

#### 删除记录

**接口**：`DELETE /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}`

---

## 五、字段类型说明

飞书多维表格支持28种字段类型，其中24种支持API写入。

### 5.1 支持写入的字段类型

| 类型 | 数据格式 | 示例 |
|------|---------|------|
| 文本 | 字符串 | `"张三"` |
| 数字 | 数值 | `12345` |
| 单选 | 字符串 | `"选项A"` |
| 多选 | 字符串数组 | `["选项A", "选项B"]` |
| 日期 | 毫秒时间戳 | `1699200000000` |
| 复选框 | 布尔值 | `true` |
| 人员 | 用户ID数组 | `[{"id": "ou_xxx"}]` |
| 电话 | 字符串 | `"13800138000"` |
| 邮箱 | 字符串 | `"test@example.com"` |
| 超链接 | 对象 | `{"link": "https://...", "text": "链接"}` |
| 附件 | 文件token数组 | `[{"file_token": "xxx"}]` |
| 地理位置 | 字符串（经纬度） | `"116.397428,39.90923"` |
| 货币 | 数值 | `99.99` |
| 进度 | 数值(0-1) | `0.75` |
| 评分 | 数值 | `5` |
| 群组 | 群组ID | `[{"id": "oc_xxx"}]` |

### 5.2 不支持API写入的字段类型

- 公式（自动计算）
- 流程
- 创建时间（自动生成）
- 修改时间（自动生成）
- 自动编号
- 按钮

---

## 六、Python实现示例

```python
import httpx
from datetime import datetime
from typing import Optional

class FeishuBitableClient:
    """飞书多维表格API客户端"""

    BASE_URL = "https://open.feishu.cn/open-apis"

    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    async def get_access_token(self) -> str:
        """获取tenant_access_token"""
        if self._access_token and self._token_expires_at > datetime.now():
            return self._access_token

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.BASE_URL}/auth/v3/tenant_access_token/internal",
                json={
                    "app_id": self.app_id,
                    "app_secret": self.app_secret
                }
            )
            data = resp.json()
            self._access_token = data["tenant_access_token"]
            self._token_expires_at = datetime.now() + timedelta(seconds=data["expire"] - 300)
            return self._access_token

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        """发送API请求"""
        token = await self.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            resp = await client.request(
                method,
                f"{self.BASE_URL}{path}",
                headers=headers,
                **kwargs
            )
            return resp.json()

    async def create_record(
        self,
        app_token: str,
        table_id: str,
        fields: dict
    ) -> dict:
        """新增单条记录"""
        return await self._request(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records",
            json={"fields": fields}
        )

    async def batch_create_records(
        self,
        app_token: str,
        table_id: str,
        records: list[dict]
    ) -> dict:
        """批量新增记录"""
        return await self._request(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create",
            json={"records": [{"fields": r} for r in records]}
        )

    async def update_record(
        self,
        app_token: str,
        table_id: str,
        record_id: str,
        fields: dict
    ) -> dict:
        """更新记录"""
        return await self._request(
            "PUT",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}",
            json={"fields": fields}
        )

    async def list_records(
        self,
        app_token: str,
        table_id: str,
        page_size: int = 100,
        page_token: str = None,
        filter_expr: str = None
    ) -> dict:
        """查询记录列表"""
        params = {"page_size": page_size}
        if page_token:
            params["page_token"] = page_token
        if filter_expr:
            params["filter"] = filter_expr

        return await self._request(
            "GET",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records",
            params=params
        )

    async def delete_record(
        self,
        app_token: str,
        table_id: str,
        record_id: str
    ) -> dict:
        """删除记录"""
        return await self._request(
            "DELETE",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
        )
```

---

## 七、候选人数据字段映射

针对Boss直聘已打招呼候选人的数据，建议创建以下字段：

| 字段名称 | 字段类型 | 说明 |
|---------|---------|------|
| 候选人姓名 | 文本 | 候选人名称 |
| 当前职位 | 文本 | 候选人当前职位 |
| 当前公司 | 文本 | 候选人当前公司 |
| 工作年限 | 文本 | 工作经验 |
| 学历 | 单选 | 学历水平 |
| 期望薪资 | 文本 | 薪资范围 |
| 打招呼职位 | 文本 | 招聘的职位名称 |
| 打招呼时间 | 日期 | 发送打招呼的时间 |
| 招呼语内容 | 多行文本 | 发送的招呼语 |
| 候选人状态 | 单选 | 已发送/已查看/已回复/已拒绝 |
| Boss直聘ID | 文本 | 候选人唯一标识 |
| 简历链接 | 超链接 | 候选人简历页面URL |
| 备注 | 多行文本 | 其他备注信息 |

---

## 八、错误处理

### 8.1 常见错误码

| 错误码 | 说明 | 处理方式 |
|-------|------|---------|
| 99991663 | access_token过期 | 重新获取token |
| 99991668 | 无权限 | 检查应用权限配置 |
| 1254043 | 记录不存在 | 检查record_id |
| 1254045 | 字段不存在 | 检查字段名是否正确 |

### 8.2 重试机制

建议实现指数退避重试：
- 第1次重试：等待1秒
- 第2次重试：等待2秒
- 第3次重试：等待4秒
- 最多重试3次

---

## 九、使用限制

- **频率限制**：100次/秒/应用
- **批量操作**：单次最多500条记录
- **分页大小**：最大500条/页
- **Token有效期**：2小时

---

## 十、配置项

在项目配置中需添加以下环境变量：

```env
# 飞书应用配置
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx

# 多维表格配置
FEISHU_BITABLE_APP_TOKEN=xxx
FEISHU_BITABLE_TABLE_ID=xxx
```

---

## 参考资料

- [飞书开放平台官方文档](https://open.feishu.cn/document?lang=zh-CN)
- [多维表格API概述](https://open.feishu.cn/document/server-docs/docs/bitable-v1/bitable-overview)
- [飞书API使用入门](https://open.feishu.cn/community/articles/7298446935350231044)
