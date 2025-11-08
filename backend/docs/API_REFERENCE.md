# Boss 直聘自动化 API 参考文档

## 概述

本文档描述了 Boss 直聘自动化系统的后端 API 接口。

- **Base URL**: `http://localhost:27421`
- **API 文档**: `http://localhost:27421/docs` (Swagger UI)
- **ReDoc**: `http://localhost:27421/redoc`

## 健康检查

### GET /api/health

检查 API 服务状态。

**响应示例**:
```json
{
  "status": "ok",
  "message": "Boss直聘自动化API运行正常"
}
```

---

## 自动化任务 API (`/api/automation`)

### POST /api/automation/tasks

创建新的自动化任务。

**请求体**:
```json
{
  "search_keywords": "Python开发工程师",
  "filters": "{\"city\":\"101020100\",\"experience\":\"103\"}",
  "greeting_template_id": 1,
  "max_contacts": 50,
  "delay_min": 2,
  "delay_max": 5
}
```

**响应**: `AutomationTask` 对象

### GET /api/automation/tasks

获取任务列表。

**查询参数**:
- `status` (可选): 任务状态筛选
- `limit` (默认: 50): 返回数量限制
- `offset` (默认: 0): 分页偏移

**响应**: `AutomationTask[]`

### GET /api/automation/tasks/{task_id}

获取任务详情。

**路径参数**:
- `task_id`: 任务 ID

**响应**: `AutomationTask` 对象

### POST /api/automation/tasks/{task_id}/start

启动任务。

**响应**:
```json
{
  "message": "任务已启动",
  "task_id": 1
}
```

### POST /api/automation/tasks/{task_id}/pause

暂停任务。

**响应**:
```json
{
  "message": "任务已暂停",
  "task_id": 1
}
```

### POST /api/automation/tasks/{task_id}/cancel

取消任务。

**响应**:
```json
{
  "message": "任务已取消",
  "task_id": 1
}
```

### DELETE /api/automation/tasks/{task_id}

删除任务（不能删除正在运行的任务）。

**响应**:
```json
{
  "message": "任务已删除",
  "task_id": 1
}
```

### GET /api/automation/status

获取自动化服务状态。

**响应**:
```json
{
  "service_initialized": true,
  "is_logged_in": true,
  "current_task_id": 1
}
```

### POST /api/automation/login

触发登录流程。

**响应**:
```json
{
  "message": "登录成功",
  "logged_in": true
}
```

### POST /api/automation/cleanup

清理自动化服务（有任务运行时无法清理）。

**响应**:
```json
{
  "message": "服务已清理"
}
```

---

## 候选人管理 API (`/api/candidates`)

### POST /api/candidates

创建候选人。

**请求体**:
```json
{
  "boss_id": "abc123",
  "name": "张三",
  "position": "Python开发工程师",
  "company": "某科技公司",
  "status": "new"
}
```

**响应**: `Candidate` 对象

### GET /api/candidates

获取候选人列表。

**查询参数**:
- `status` (可选): 状态筛选
- `search` (可选): 搜索关键词
- `limit` (默认: 50): 返回数量限制
- `offset` (默认: 0): 分页偏移

**响应**: `Candidate[]`

### GET /api/candidates/stats

获取候选人统计信息。

**响应**:
```json
{
  "total": 100,
  "today_added": 5,
  "by_status": {
    "new": 20,
    "contacted": 50,
    "replied": 15,
    "interested": 10,
    "rejected": 3,
    "archived": 2
  }
}
```

### GET /api/candidates/{candidate_id}

获取候选人详情。

**响应**: `Candidate` 对象

### PATCH /api/candidates/{candidate_id}

更新候选人信息。

**请求体**:
```json
{
  "status": "contacted",
  "notes": "已发送问候消息"
}
```

**响应**: `Candidate` 对象

### DELETE /api/candidates/{candidate_id}

删除候选人（有问候记录的无法删除）。

**响应**:
```json
{
  "message": "候选人已删除",
  "candidate_id": 1
}
```

### GET /api/candidates/{candidate_id}/greetings

获取候选人的问候记录。

**响应**: `GreetingRecord[]`

### POST /api/candidates/{candidate_id}/archive

归档候选人。

**响应**:
```json
{
  "message": "候选人已归档",
  "candidate_id": 1
}
```

### POST /api/candidates/batch/update-status

批量更新候选人状态。

**请求体**:
```json
{
  "candidate_ids": [1, 2, 3],
  "status": "archived"
}
```

**响应**:
```json
{
  "message": "已更新 3 个候选人状态",
  "updated_count": 3
}
```

### POST /api/candidates/batch/delete

批量删除候选人。

**请求体**:
```json
{
  "candidate_ids": [1, 2, 3]
}
```

**响应**:
```json
{
  "message": "已删除 3 个候选人",
  "deleted_count": 3
}
```

---

## 问候模板 API (`/api/templates`)

### POST /api/templates

创建问候模板。

**请求体**:
```json
{
  "name": "通用问候模板",
  "content": "你好 {name}，看到你是 {position}，我们这里有一个很好的机会...",
  "is_active": true
}
```

**响应**: `GreetingTemplate` 对象

### GET /api/templates

获取模板列表。

**查询参数**:
- `is_active` (可选): 激活状态筛选
- `limit` (默认: 50): 返回数量限制
- `offset` (默认: 0): 分页偏移

**响应**: `GreetingTemplate[]`

### GET /api/templates/active

获取所有激活的模板。

**响应**: `GreetingTemplate[]`

### GET /api/templates/{template_id}

获取模板详情。

**响应**: `GreetingTemplate` 对象

### PATCH /api/templates/{template_id}

更新模板。

**请求体**:
```json
{
  "name": "更新后的模板名称",
  "content": "更新后的内容"
}
```

**响应**: `GreetingTemplate` 对象

### DELETE /api/templates/{template_id}

删除模板（正在使用的模板无法删除）。

**响应**:
```json
{
  "message": "模板已删除",
  "template_id": 1
}
```

### POST /api/templates/{template_id}/activate

激活模板。

**响应**:
```json
{
  "message": "模板已激活",
  "template_id": 1
}
```

### POST /api/templates/{template_id}/deactivate

停用模板。

**响应**:
```json
{
  "message": "模板已停用",
  "template_id": 1
}
```

### POST /api/templates/{template_id}/duplicate

复制模板。

**响应**: `GreetingTemplate` 对象（新创建的副本）

### GET /api/templates/{template_id}/preview

预览模板效果。

**查询参数**:
- `name`: 候选人姓名
- `position`: 职位
- `company` (可选): 公司

**响应**:
```json
{
  "template_id": 1,
  "template_name": "通用问候模板",
  "original_content": "你好 {name}，看到你是 {position}...",
  "preview_content": "你好 张三，看到你是 Python开发工程师...",
  "variables_used": {
    "name": "张三",
    "position": "Python开发工程师",
    "company": null
  }
}
```

### POST /api/templates/batch/delete

批量删除模板。

**请求体**:
```json
{
  "template_ids": [1, 2, 3]
}
```

**响应**:
```json
{
  "message": "已删除 3 个模板",
  "deleted_count": 3
}
```

---

## 系统配置 API (`/api/config`)

### GET /api/config

获取系统配置。

**响应**: `SystemConfig` 对象

### PATCH /api/config

更新系统配置。

**请求体**:
```json
{
  "daily_limit": 150,
  "auto_mode_enabled": true,
  "rest_interval": 20,
  "rest_duration": 90
}
```

**响应**: `SystemConfig` 对象

### POST /api/config/reset-daily-counter

重置每日联系计数。

**响应**:
```json
{
  "message": "每日计数已重置",
  "today_contacted": 0
}
```

### POST /api/config/increment-daily-counter

增加每日联系计数（自动检查是否新的一天）。

**响应**:
```json
{
  "message": "计数已增加",
  "today_contacted": 5,
  "daily_limit": 100
}
```

### GET /api/config/check-daily-limit

检查是否达到每日限制。

**响应**:
```json
{
  "reached_limit": false,
  "today_contacted": 50,
  "daily_limit": 100,
  "remaining": 50
}
```

### POST /api/config/toggle-auto-mode

切换自动模式。

**响应**:
```json
{
  "message": "自动模式已启用",
  "auto_mode_enabled": true
}
```

### POST /api/config/toggle-anti-detection

切换反检测模式。

**响应**:
```json
{
  "message": "反检测模式已启用",
  "anti_detection_enabled": true
}
```

### POST /api/config/toggle-random-delay

切换随机延迟。

**响应**:
```json
{
  "message": "随机延迟已启用",
  "random_delay_enabled": true
}
```

### POST /api/config/save-login-info

保存登录信息。

**查询参数**:
- `username` (可选): Boss 用户名

**响应**:
```json
{
  "message": "登录信息已保存",
  "boss_username": "example@email.com",
  "boss_session_saved": true
}
```

### POST /api/config/clear-login-info

清除登录信息（同时删除保存的登录状态文件）。

**响应**:
```json
{
  "message": "登录信息已清除",
  "boss_session_saved": false
}
```

### GET /api/config/stats

获取系统统计信息（包括候选人、问候、任务、模板的统计数据）。

**响应**:
```json
{
  "config": {
    "auto_mode_enabled": false,
    "daily_limit": 100,
    "today_contacted": 10,
    "remaining_today": 90,
    "boss_session_saved": true,
    "anti_detection_enabled": true
  },
  "candidates": {
    "total": 150,
    "today_added": 5
  },
  "greetings": {
    "total": 120,
    "success": 115,
    "success_rate": 95.83,
    "today": 10
  },
  "tasks": {
    "total": 20,
    "running": 1,
    "completed": 15
  },
  "templates": {
    "total": 5,
    "active": 3
  }
}
```

---

## 数据模型

### CandidateStatus (枚举)

候选人状态：
- `new`: 新候选人
- `contacted`: 已联系
- `replied`: 已回复
- `interested`: 感兴趣
- `rejected`: 已拒绝
- `archived`: 已归档

### TaskStatus (枚举)

任务状态：
- `pending`: 待处理
- `running`: 运行中
- `paused`: 已暂停
- `completed`: 已完成
- `failed`: 失败
- `cancelled`: 已取消

### 模板变量

问候模板支持以下变量：
- `{name}`: 候选人姓名
- `{position}`: 职位
- `{company}`: 公司（可选）

---

## 错误处理

所有 API 错误响应遵循以下格式：

```json
{
  "detail": "错误描述信息"
}
```

常见 HTTP 状态码：
- `200`: 成功
- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器内部错误

---

## 使用示例

### 创建并启动一个自动化任务

1. 创建问候模板：
```bash
curl -X POST http://localhost:27421/api/templates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Python开发问候",
    "content": "你好 {name}，看到你是 {position}，我们有个很好的机会...",
    "is_active": true
  }'
```

2. 创建自动化任务：
```bash
curl -X POST http://localhost:27421/api/automation/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "search_keywords": "Python开发",
    "filters": "{}",
    "greeting_template_id": 1,
    "max_contacts": 20,
    "delay_min": 2,
    "delay_max": 5
  }'
```

3. 启动任务：
```bash
curl -X POST http://localhost:27421/api/automation/tasks/1/start
```

4. 查看任务进度：
```bash
curl http://localhost:27421/api/automation/tasks/1
```

---

## 注意事项

1. **登录状态**: 使用自动化功能前，需要先调用 `/api/automation/login` 完成登录
2. **每日限制**: 系统会自动跟踪每日联系数量，达到限制后会阻止继续联系
3. **反检测**: 建议启用反检测和随机延迟功能，避免被识别为机器人
4. **并发任务**: 同一时间只能运行一个自动化任务
5. **数据持久化**: 所有数据存储在 SQLite 数据库中 (`database.db`)
6. **登录状态保存**: 登录状态保存在 `boss_auth.json` 文件中

---

## 开发文档

访问 `http://localhost:27421/docs` 可以查看交互式 API 文档（Swagger UI），支持直接在浏览器中测试 API。
