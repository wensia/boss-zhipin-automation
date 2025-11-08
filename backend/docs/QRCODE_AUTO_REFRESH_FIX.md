# 二维码自动刷新功能修复

## 问题描述

**用户反馈**：
1. 提供了正确的二维码元素选择器: `#wrap > div > div.login-entry-page > div.login-register-content > div.scan-app-wrapper > div.qr-code-box > div.qr-img-box > img`
2. 指出没有采用"过期轮询点击"功能
3. 二维码可能抓取错误

## 问题分析

### 发现的问题

1. **缺少过期检测**:
   - 代码中已经有 `check_and_refresh_qrcode()` 方法用于检测和刷新过期二维码
   - 但是在 `get_qrcode()` 方法中没有调用这个检测逻辑
   - 导致即使二维码过期了，也不会自动刷新

2. **工作流程不完整**:
   - 之前: `get_qrcode()` → 直接读取二维码
   - 问题: 如果二维码已过期，会读取到过期的二维码或刷新按钮

### 现有的刷新机制

`check_and_refresh_qrcode()` 方法（第439-517行）的功能：
- 检测页面是否在登录界面
- 查找刷新按钮（二维码过期时会出现）
- 如果发现刷新按钮，自动点击
- 等待新二维码加载
- 返回新的二维码URL

**刷新按钮选择器**: `#wrap > div > div.login-entry-page > div.login-register-content > div.scan-app-wrapper > div.qr-code-box > div.qr-img-box > div > button`

## 修复内容

### 修改了 `get_qrcode()` 方法

**文件**: `app/services/boss_automation.py`
**行数**: 383-419

**修改前逻辑**:
```python
# 如果在登录页面，读取二维码
if 'zhipin.com/web/user/' in current_url:
    logger.info("📋 当前在登录页面，读取二维码...")

    # 直接查找并读取二维码元素
    qrcode_element = await self.page.wait_for_selector(qrcode_img_selector, timeout=3000)
    # ... 读取 src 属性并返回
```

**修改后逻辑**:
```python
# 如果在登录页面，读取二维码
if 'zhipin.com/web/user/' in current_url:
    logger.info("📋 当前在登录页面，读取二维码...")

    # 1. 先检查二维码是否过期
    logger.info("🔍 检查二维码是否需要刷新...")
    refresh_result = await self.check_and_refresh_qrcode()

    # 2. 如果检测到过期并成功刷新，直接返回新二维码
    if refresh_result.get('need_refresh') and refresh_result.get('qrcode'):
        logger.info("✅ 二维码已自动刷新")
        return {
            'success': True,
            'qrcode': refresh_result.get('qrcode'),
            'message': '二维码已刷新'
        }

    # 3. 如果不需要刷新，正常读取二维码
    qrcode_element = await self.page.wait_for_selector(qrcode_img_selector, timeout=5000)
    # ... 读取 src 属性并返回
```

### 关键改进

1. **自动检测过期**: 每次调用 `get_qrcode()` 时，先检查是否有刷新按钮
2. **自动刷新**: 如果检测到过期（有刷新按钮），自动点击刷新
3. **返回新二维码**: 刷新成功后，直接返回新的二维码URL
4. **增加超时**: 将二维码元素等待时间从 3秒 增加到 5秒，更可靠

## 工作流程

### 完整的二维码获取流程

```
1. 前端调用 /api/automation/qrcode
   ↓
2. get_qrcode() 检查浏览器状态
   ↓
3. 检查当前URL是否在登录页面
   ↓
4. 调用 check_and_refresh_qrcode()
   ├─ 查找刷新按钮
   │  ├─ 找到 → 二维码已过期
   │  │  ├─ 点击刷新按钮
   │  │  ├─ 等待新二维码加载
   │  │  └─ 返回新二维码
   │  └─ 未找到 → 二维码有效
   │     └─ 继续正常读取
   ↓
5. 读取二维码图片的 src 属性
   ↓
6. 转换为完整URL（如果是相对路径）
   ↓
7. 返回给前端显示
```

## 测试方法

### 测试场景1: 正常二维码

1. 初始化浏览器
2. 点击"获取二维码"
3. **预期**: 直接读取并显示二维码
4. **日志应显示**:
   ```
   📋 当前在登录页面，读取二维码...
   🔍 检查二维码是否需要刷新...
   ✅ 成功读取二维码
   ```

### 测试场景2: 过期二维码

1. 初始化浏览器并获取二维码
2. 等待二维码过期（约2-3分钟）
3. 再次点击"获取二维码"
4. **预期**: 自动检测到过期，点击刷新，返回新二维码
5. **日志应显示**:
   ```
   📋 当前在登录页面，读取二维码...
   🔍 检查二维码是否需要刷新...
   🔄 检测到二维码过期，自动刷新...
   ✅ 二维码已刷新
   ✅ 二维码已自动刷新
   ```

### 测试场景3: 刷新失败降级

1. 如果刷新失败，会继续尝试正常读取
2. 确保不会因为刷新失败而完全无法获取二维码

## 相关选择器

### 二维码图片
```css
#wrap > div > div.login-entry-page > div.login-register-content > div.scan-app-wrapper > div.qr-code-box > div.qr-img-box > img
```

### 刷新按钮（二维码过期时出现）
```css
#wrap > div > div.login-entry-page > div.login-register-content > div.scan-app-wrapper > div.qr-code-box > div.qr-img-box > div > button
```

### 二维码切换按钮
```css
#wrap > div > div.login-entry-page > div.login-register-content > div.btn-sign-switch.ewm-switch
```

## 后续优化建议

1. **前端轮询**: 可以在前端添加定时器，每隔30秒自动调用 `/api/automation/qrcode` 获取新二维码
2. **过期提示**: 在刷新时给用户更明显的提示
3. **WebSocket推送**: 考虑使用WebSocket实时推送二维码更新
4. **过期倒计时**: 显示二维码剩余有效时间

## 文件变更

- `app/services/boss_automation.py` (第383-419行) - 修改 `get_qrcode()` 方法，添加过期检测和自动刷新逻辑

## 预期效果

### 修复前
- ❌ 二维码过期后，需要手动刷新页面
- ❌ 用户体验差，可能扫描到过期二维码
- ❌ 需要前端手动实现刷新逻辑

### 修复后
- ✅ 自动检测二维码是否过期
- ✅ 自动点击刷新按钮获取新二维码
- ✅ 用户始终获取到有效的二维码
- ✅ 提升用户体验，无需手动干预
