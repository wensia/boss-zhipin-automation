# 自动打招呼功能修复说明

## ✅ 问题修复

### 原问题
用户在向导中已经：
1. 初始化了浏览器
2. 登录了Boss直聘
3. 选择了职位
4. 应用了筛选条件
5. **已经在推荐候选人页面**

但点击"开始打招呼"后，系统会创建新的浏览器会话并跳转页面，而不是使用当前已经打开的页面。

### 修复方案

#### 1. **复用浏览器会话** (`app/services/greeting_service.py`)

**修改前**：
```python
# 创建新的浏览器实例
self.automation = GreetingAutomation(headless=False)
await self.automation.initialize(auth_file=auth_file)
```

**修改后**：
```python
# 接收外部传入的已初始化BossAutomation实例
async def start_greeting_task(self, target_count: int, automation_service=None):
    self.automation = automation_service  # 复用已有浏览器
```

#### 2. **直接操作当前页面的候选人列表**

**新的执行流程**：
```python
# 1. 获取recommendFrame（用户已在推荐页面）
recommend_frame = None
for frame in self.automation.page.frames:
    if frame.name == 'recommendFrame':
        recommend_frame = frame
        break

# 2. 直接查找当前页面的候选人列表
candidate_selector = 'ul.candidate-list > li'
candidates = await recommend_frame.locator(candidate_selector).all()

# 3. 点击候选人卡片
candidate = candidates[i]
await candidate.click()

# 4. 在recommendFrame中点击打招呼按钮
button = recommend_frame.locator('.dialog-lib-resume .button-list-wrap button').first
await button.click()

# 5. 关闭简历面板
close_btn = recommend_frame.locator('.dialog-lib-resume .close-icon').first
await close_btn.click()

# 6. 继续下一个候选人
```

#### 3. **传入全局自动化服务** (`app/routes/greeting.py`)

**修改前**：
```python
await greeting_manager.start_greeting_task(
    target_count=request.target_count,
    auth_file="boss_auth.json"  # 会创建新浏览器
)
```

**修改后**：
```python
# 获取全局自动化服务（复用已打开的浏览器）
automation = await get_automation_service()

# 验证浏览器已初始化和登录
if not automation.is_logged_in:
    raise HTTPException(status_code=401, detail="未登录，请先在向导中完成登录")

# 传入已有的自动化服务
await greeting_manager.start_greeting_task(
    target_count=request.target_count,
    automation_service=automation
)
```

#### 4. **不关闭浏览器** (`app/services/greeting_service.py`)

**修改前**：
```python
finally:
    if self.automation:
        await self.automation.close()  # 关闭浏览器
```

**修改后**：
```python
finally:
    # 不要关闭浏览器，因为是复用的全局实例
    pass
```

## 🎯 正确的使用流程

### 用户操作步骤：

1. **在自动化向导页面** (`/wizard`)：
   - 初始化浏览器（显示/隐藏模式）
   - 扫码登录Boss直聘
   - 选择招聘职位
   - 配置筛选条件
   - 应用筛选（此时已在推荐候选人页面）

2. **切换到自动打招呼页面** (`/greeting`)：
   - 输入打招呼数量（1-100）
   - 点击"开始"按钮
   - **系统会直接在当前已打开的页面操作**
   - **不会创建新浏览器或跳转页面**

3. **自动执行流程**：
   - 找到当前页面的候选人列表（ul元素）
   - 点击候选人卡片（li元素）
   - 等待简历面板加载
   - 在recommendFrame中点击打招呼按钮
   - 等待按钮状态变化
   - 点击右上角关闭按钮
   - 回到候选人列表
   - 继续下一个候选人

## 📊 技术细节

### 关键点1：复用全局BossAutomation实例

```python
# app/routes/automation.py
_automation_service: Optional[BossAutomation] = None  # 全局单例

async def get_automation_service() -> BossAutomation:
    global _automation_service
    if _automation_service is None:
        _automation_service = BossAutomation()
        await _automation_service.initialize()
    return _automation_service
```

### 关键点2：在recommendFrame中操作

所有操作都在 `recommendFrame` 中进行：
- 候选人列表：`ul.candidate-list > li`
- 打招呼按钮：`.dialog-lib-resume .button-list-wrap button`
- 关闭按钮：`.dialog-lib-resume .close-icon`

### 关键点3：自动滚动加载

```python
if i >= len(candidates):
    # 滚动加载更多候选人
    await recommend_frame.evaluate('window.scrollTo(0, document.body.scrollHeight)')
    await asyncio.sleep(2)
    candidates = await recommend_frame.locator(candidate_selector).all()
```

## ✨ 优点

1. **无缝体验**：用户无需重新初始化浏览器或重新登录
2. **快速响应**：直接操作当前页面，无需等待页面跳转
3. **资源节约**：复用已有浏览器会话，不创建新进程
4. **状态保持**：保留用户在向导中的所有配置（职位、筛选条件）
5. **符合预期**：完全按照用户描述的流程执行

## 🔍 验证方法

### 测试步骤：
1. 访问 `/wizard` 完成向导配置
2. 确保浏览器停留在推荐候选人页面
3. 访问 `/greeting` 输入数量并点击开始
4. **观察：浏览器不会创建新窗口，直接在当前页面操作候选人列表**
5. 查看日志，应该看到：
   ```
   ✅ 使用已打开的浏览器
   ✅ 找到推荐页面iframe
   点击候选人: XXX
   ✅ 简历面板已加载
   找到按钮: '打招呼'
   ✅ 已点击【打招呼】按钮
   ✅ 已关闭简历面板
   ✅ 候选人 1 处理成功
   ```

## 📝 相关文件

- `backend/app/services/greeting_service.py` - 打招呼任务管理器
- `backend/app/routes/greeting.py` - 打招呼API路由
- `backend/app/routes/automation.py` - 全局自动化服务
- `frontend/src/pages/auto-greeting.tsx` - 打招呼前端页面

---

**修复日期**: 2025-10-29
**版本**: v2.0.0 (Browser Reuse)
