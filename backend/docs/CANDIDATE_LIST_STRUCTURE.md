# Boss直聘 候选人列表结构分析文档

## 📋 概述

本文档详细记录了Boss直聘推荐候选人列表页面的DOM结构、交互逻辑和滚动加载机制。

**测试日期**: 2025-10-29
**测试URL**: `https://www.zhipin.com/web/chat/recommend`
**测试方法**: Playwright 自动化脚本

---

## 🏗️ 页面结构

### 1. 页面层级

```
Main Page (https://www.zhipin.com/web/chat/recommend)
  └── iframe#recommendFrame (name="recommendFrame")
       └── https://www.zhipin.com/web/frame/recommend/?filterParams=...
            └── #recommend-list
                 └── div.list-body
                      └── ul.card-list
                           └── li.card-item (候选人卡片)
```

### 2. iframe 信息

**主页面 (Main Frame)**:
- URL: `https://www.zhipin.com/web/chat/recommend`
- Frame Count: 2 (主页面 + recommendFrame)

**候选人列表 iframe**:
- **Name**: `recommendFrame` ⭐ (查找 iframe 的关键标识)
- **URL 格式**: `https://www.zhipin.com/web/frame/recommend/?filterParams=&t=&inspectFilterGuide=&version=8590&status=0&jobid=...&source=0`
- **作用**: 包含完整的候选人列表和筛选功能

### 3. 访问 iframe 的代码

```python
# Playwright 代码示例
frames = page.frames
recommend_frame = None

for frame in frames:
    if frame.name == 'recommendFrame':
        recommend_frame = frame
        break

if not recommend_frame:
    raise Exception("未找到 recommendFrame")
```

---

## 📦 候选人列表元素结构

### 1. 容器选择器

| 选择器 | 元素 | 类名 | 说明 |
|--------|------|------|------|
| `#recommend-list` | `<div>` | `list-wrap card-list-wrap` | 列表外层容器 |
| `#recommend-list > div` | `<div>` | `list-body` | 列表主体容器 |
| `#recommend-list > div > ul` | `<ul>` | `card-list` | 候选人卡片列表 |
| `ul.card-list > li` | `<li>` | `card-item` | 单个候选人卡片 ⭐ |

### 2. 候选人卡片选择器 (推荐使用)

```javascript
// 最佳选择器（稳定可靠）
const cards = document.querySelectorAll('ul.card-list > li');

// 或者使用完整路径
const cards = document.querySelectorAll('#recommend-list > div > ul > li');

// 或者使用类名
const cards = document.querySelectorAll('.card-list > li');
const cards = document.querySelectorAll('li.card-item');
```

### 3. 候选人卡片属性

- **标签**: `<li>`
- **类名**: `card-item`
- **data 属性**: `data-v-b753c1ac=""` (Vue.js 组件标识)
- **选择器模板**: `ul.card-list > li:nth-child(N)` (N 从 1 开始)

---

## 🎯 候选人卡片数据结构

### 1. 示例数据

```javascript
{
  "姓名": "李嘉昕",
  "年龄": "28岁",
  "工作经验": "3年",
  "学历": "本科",
  "求职状态": "离职-随时到岗",
  "期望薪资": "4-9K",
  "期望城市": "天津",
  "期望职位": "新媒体运营",
  "优势": "能力方面：有多年海外留学经验...",
  "活跃时间": "2024.09-2025.05"
}
```

### 2. 提取候选人信息的代码

```javascript
const card = document.querySelector('ul.card-list > li:nth-child(1)');

// 提取卡片文本
const text = card.textContent.trim();

// 提取特定字段（根据实际DOM结构调整）
const name = card.querySelector('.geek-name, .name, h3')?.textContent.trim();
const position = card.querySelector('.geek-position, .position, .job-title')?.textContent.trim();
const company = card.querySelector('.geek-company, .company')?.textContent.trim();
const activeTime = card.querySelector('.geek-active-time, .active-time, .time')?.textContent.trim();

// 获取完整文本（前100个字符）
const preview = card.textContent.substring(0, 100);
```

### 3. 批量获取所有候选人

```javascript
const candidates = [];
const cards = document.querySelectorAll('ul.card-list > li');

cards.forEach((card, index) => {
  candidates.push({
    index: index,
    selector: `ul.card-list > li:nth-child(${index + 1})`,
    text: card.textContent.substring(0, 100),
    className: card.className,
    dataAttributes: Array.from(card.attributes)
      .filter(attr => attr.name.startsWith('data-'))
      .map(attr => ({ name: attr.name, value: attr.value }))
  });
});

console.log(`找到 ${candidates.length} 个候选人`);
```

---

## 🖱️ 点击候选人卡片

### 1. 点击行为

- **URL 变化**: ❌ 不变 (保持在 `/web/chat/recommend`)
- **页面跳转**: ❌ 无跳转
- **详情展示方式**: ✅ 在当前页面打开详情面板 (新增 iframe)
- **Frame 数量变化**: 3 → 4 (新增一个详情 iframe)

### 2. 点击代码示例

```python
# Playwright 代码
candidate_cards = await recommend_frame.query_selector_all('ul.card-list > li')

if len(candidate_cards) > 0:
    # 点击第一个候选人
    await candidate_cards[0].click()
    await asyncio.sleep(2)

    # 点击后会打开详情面板（新的 iframe）
    # 无需 page.go_back()，因为没有导航发生
```

### 3. 关闭详情面板

```python
# 尝试查找并点击关闭按钮
close_button = await page.query_selector('.close, .close-btn, .icon-close')
if close_button:
    await close_button.click()
    await asyncio.sleep(1)
```

---

## 🔄 滚动加载机制

### 1. 滚动容器

**重要发现**:
- ❌ `#recommend-list` 不是滚动容器 (overflow-y: visible)
- ❌ `#recommend-list > div` 不是滚动容器 (overflow-y: visible)
- ✅ **iframe 的 document 本身是滚动容器**

### 2. 滚动容器属性

```javascript
{
  "scrollHeight": 2948,    // 内容总高度
  "clientHeight": 2948,    // 可见区域高度
  "scrollTop": 0,          // 当前滚动位置
  "isScrollable": false,   // #recommend-list 不可滚动
  "overflowY": "visible"   // 溢出样式
}
```

### 3. 正确的滚动方法

```javascript
// ✅ 正确：滚动 iframe 的 window
await recommend_frame.evaluate(() => {
  window.scrollTo({
    top: document.documentElement.scrollHeight,
    behavior: 'smooth'
  });
});

// ❌ 错误：尝试滚动列表容器
await recommend_frame.evaluate(() => {
  const container = document.querySelector('#recommend-list');
  container.scrollTo({ top: container.scrollHeight });  // 不会生效
});
```

### 4. 滚动加载效果

**测试结果**:
- **初始加载**: 15 个候选人
- **滚动 3 次后**: 60 个候选人
- **新增候选人**: 45 个
- **加载方式**: 懒加载 (Lazy Loading)

### 5. 完整滚动加载代码

```python
# 获取初始候选人数量
initial_count = len(await recommend_frame.query_selector_all('ul.card-list > li'))
print(f"初始候选人数量: {initial_count}")

# 执行滚动加载
for i in range(3):
    await recommend_frame.evaluate("""
        () => {
            window.scrollTo({
                top: document.documentElement.scrollHeight,
                behavior: 'smooth'
            });
        }
    """)
    await asyncio.sleep(2)  # 等待加载

# 获取滚动后的候选人数量
final_count = len(await recommend_frame.query_selector_all('ul.card-list > li'))
print(f"滚动后候选人数量: {final_count}")
print(f"新增候选人: {final_count - initial_count}")
```

---

## 🔍 完整工作流程示例

### Python + Playwright 完整示例

```python
import asyncio
from playwright.async_api import async_playwright

async def get_candidates():
    """获取候选人列表的完整流程"""

    async with async_playwright() as p:
        # 1. 启动浏览器
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )

        # 2. 加载登录状态
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            storage_state='boss_auth.json'  # 需要先登录并保存状态
        )
        page = await context.new_page()

        # 3. 导航到推荐页面
        await page.goto('https://www.zhipin.com/web/chat/recommend', wait_until='networkidle')
        await asyncio.sleep(3)

        # 4. 查找 recommendFrame iframe
        recommend_frame = None
        for frame in page.frames:
            if frame.name == 'recommendFrame':
                recommend_frame = frame
                break

        if not recommend_frame:
            raise Exception("未找到 recommendFrame")

        # 5. 等待候选人列表加载
        await asyncio.sleep(2)

        # 6. 获取候选人卡片
        candidates = await recommend_frame.query_selector_all('ul.card-list > li')
        print(f"找到 {len(candidates)} 个候选人")

        # 7. 提取候选人数据
        candidates_data = []
        for i, card in enumerate(candidates):
            text = await card.text_content()
            candidates_data.append({
                'index': i,
                'text': text.strip()[:100]
            })

        # 8. 滚动加载更多候选人
        for scroll_round in range(3):
            await recommend_frame.evaluate("window.scrollTo({top: document.documentElement.scrollHeight, behavior: 'smooth'})")
            await asyncio.sleep(2)

        # 9. 重新获取候选人数量
        candidates = await recommend_frame.query_selector_all('ul.card-list > li')
        print(f"滚动后候选人数量: {len(candidates)}")

        await browser.close()
        return candidates_data

# 运行示例
if __name__ == "__main__":
    asyncio.run(get_candidates())
```

---

## 📝 重要注意事项

### 1. 认证要求

- ✅ 必须先登录 Boss直聘
- ✅ 使用 `storage_state` 保存和加载登录状态
- ❌ 未登录会重定向到 `/web/user/`

### 2. iframe 访问

- ✅ 必须通过 `frame.name == 'recommendFrame'` 查找 iframe
- ✅ 所有候选人操作都在 iframe 内执行
- ❌ 不能在主页面 (page) 上查找候选人元素

### 3. 选择器稳定性

- ✅ 推荐使用: `ul.card-list > li`
- ✅ 备选方案: `li.card-item`
- ❌ 不要使用: `li.geek-item` (不存在)
- ❌ 不要使用: `.geek-list` (不存在)

### 4. 滚动加载

- ✅ 使用 `window.scrollTo()` 在 iframe 中滚动
- ✅ 每次滚动后等待 2-3 秒让数据加载
- ❌ 不要滚动 `#recommend-list` 容器（无效）

### 5. 点击行为

- ✅ 点击卡片会打开详情面板（无导航）
- ✅ Frame 数量会从 3 增加到 4
- ❌ 不要调用 `page.go_back()` (会超时)

---

## 🎯 常见问题解决

### Q1: 找不到候选人卡片？

**原因**: 可能在错误的 frame 中查找元素

**解决方案**:
```python
# 确保在 recommendFrame 中查找
recommend_frame = None
for frame in page.frames:
    if frame.name == 'recommendFrame':
        recommend_frame = frame
        break

# 在 recommend_frame 中查找，不是 page！
cards = await recommend_frame.query_selector_all('ul.card-list > li')
```

### Q2: 滚动后没有加载更多候选人？

**原因**: 滚动的容器不对

**解决方案**:
```python
# 正确：滚动 iframe 的 window
await recommend_frame.evaluate("window.scrollTo({top: document.documentElement.scrollHeight})")

# 错误：滚动 #recommend-list
await recommend_frame.evaluate("document.querySelector('#recommend-list').scrollTo(...)")
```

### Q3: 点击卡片后 go_back() 超时？

**原因**: 点击卡片不会触发导航，只是打开详情面板

**解决方案**:
```python
# 不要调用 go_back()
await card.click()
await asyncio.sleep(2)

# 如果需要关闭详情，查找关闭按钮
close_btn = await page.query_selector('.close, .icon-close')
if close_btn:
    await close_btn.click()
```

### Q4: 页面重定向到 /web/user/？

**原因**: 未登录或登录状态过期

**解决方案**:
```python
# 加载保存的登录状态
context = await browser.new_context(
    storage_state='boss_auth.json'
)
```

---

## 🚀 快速参考

### 关键选择器

```javascript
// iframe
frame.name === 'recommendFrame'

// 候选人列表
'ul.card-list > li'          // 推荐 ⭐
'li.card-item'               // 备选
'#recommend-list > div > ul > li'  // 完整路径
```

### 关键操作

```python
# 1. 查找 iframe
recommend_frame = next((f for f in page.frames if f.name == 'recommendFrame'), None)

# 2. 获取候选人
cards = await recommend_frame.query_selector_all('ul.card-list > li')

# 3. 滚动加载
await recommend_frame.evaluate("window.scrollTo({top: document.documentElement.scrollHeight})")

# 4. 点击候选人
await cards[0].click()
```

---

## 📚 相关文档

- [Playwright 官方文档](https://playwright.dev/python/)
- [Boss直聘自动化项目](../README.md)
- [测试脚本](./test_candidate_list_explorer.py)

---

**文档版本**: v1.0
**最后更新**: 2025-10-29
**作者**: Claude Code + Boss直聘自动化项目
