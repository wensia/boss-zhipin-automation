# Boss直聘候选人信息获取脚本使用指南

## 📋 脚本说明

`get_candidates_info.py` 是一个自动化脚本，用于从Boss直聘推荐牛人页面获取候选人的详细信息，并保存为结构化的 JSON 数据。

## ✨ 功能特性

- ✅ 自动登录（使用已保存的登录状态）
- ✅ 自动滚动加载更多候选人
- ✅ 智能提取候选人关键信息
- ✅ 保存为 JSON 格式
- ✅ 统计分析（学历分布、求职状态等）
- ✅ 可配置获取数量和滚动轮数

## 📊 提取的数据字段

每个候选人的信息包括：

| 字段 | 说明 | 示例 |
|------|------|------|
| `name` | 姓名 | "李嘉昕" |
| `age` | 年龄 | 28 |
| `experience` | 工作经验 | "3年" / "25年应届生" |
| `education` | 学历 | "本科" / "硕士" / "大专" |
| `salary` | 期望薪资 | "4-9K" / "10K以上" |
| `jobStatus` | 求职状态 | "离职-随时到岗" / "在职-考虑机会" |
| `expectedCity` | 期望城市 | "天津" |
| `expectedPosition` | 期望职位 | "新媒体运营" / "平面设计" |
| `advantage` | 个人优势 | "能力方面：有多年海外留学经验..." |
| `activity` | 活跃度 | "刚刚活跃" / "今日活跃" / "3日内活跃" |
| `workStartDate` | 工作起始日期 | "2024.09" |
| `workEndDate` | 工作结束日期 | "2025.05" |
| `fullText` | 完整文本 | 卡片的完整文本内容 |
| `index` | 卡片索引 | 0, 1, 2... |
| `selector` | CSS选择器 | "ul.card-list > li:nth-child(1)" |
| `dataAttributes` | data属性 | {"data-v-b753c1ac": ""} |

## 🚀 使用方法

### 1. 前置要求

- 已安装 Python 和 Playwright
- 已有 Boss直聘 登录状态文件 (`boss_auth.json`)

### 2. 基本使用

```bash
# 运行脚本（使用默认配置）
uv run python get_candidates_info.py

# 或使用普通 Python
python get_candidates_info.py
```

### 3. 配置参数

在 `main()` 函数中可以修改以下参数：

```python
# 配置参数
MAX_CANDIDATES = None  # None = 获取所有，或设置具体数字如 20
SCROLL_ROUNDS = 3      # 滚动加载轮数，0 = 不滚动，只获取初始15个
AUTH_FILE = 'boss_auth.json'  # 登录状态文件路径
```

### 4. 输出结果

#### JSON 文件

脚本会生成 `candidates_data.json` 文件，包含所有候选人的详细信息：

```json
[
  {
    "name": "李嘉昕",
    "age": 28,
    "experience": "3年",
    "education": "本科",
    "salary": "4-9K",
    "jobStatus": "离职-随时到岗",
    "expectedCity": "天津",
    "expectedPosition": "新媒体运营",
    "advantage": "能力方面：有多年海外留学经验...",
    "activity": null,
    "workStartDate": "2024.09",
    "workEndDate": "2025.05",
    "fullText": "完整文本...",
    "index": 0,
    "selector": "ul.card-list > li:nth-child(1)",
    "dataAttributes": {
      "data-v-b753c1ac": ""
    }
  },
  ...
]
```

#### 控制台输出

脚本运行时会在控制台显示：

1. **实时进度**
   ```
   处理候选人 1/60...
     ✅ 李嘉昕 | 28岁 | 本科 | 4-9K | 新媒体运营
   ```

2. **统计信息**
   ```
   学历分布:
     本科: 35 人
     大专: 21 人
     硕士: 1 人

   求职状态分布:
     离职-随时到岗: 37 人
     在职-月内到岗: 7 人
     在职-考虑机会: 3 人
   ```

3. **示例数据**（前3个候选人的详细信息）

## 📝 使用示例

### 示例 1: 获取前20个候选人（不滚动）

```python
async def main():
    MAX_CANDIDATES = 20
    SCROLL_ROUNDS = 0
    AUTH_FILE = 'boss_auth.json'

    candidates = await get_candidates_info(
        max_candidates=MAX_CANDIDATES,
        scroll_rounds=SCROLL_ROUNDS,
        auth_file=AUTH_FILE
    )
```

### 示例 2: 获取所有候选人（滚动5轮）

```python
async def main():
    MAX_CANDIDATES = None
    SCROLL_ROUNDS = 5
    AUTH_FILE = 'boss_auth.json'

    candidates = await get_candidates_info(
        max_candidates=MAX_CANDIDATES,
        scroll_rounds=SCROLL_ROUNDS,
        auth_file=AUTH_FILE
    )
```

### 示例 3: 在代码中使用获取的数据

```python
import json

# 读取JSON文件
with open('candidates_data.json', 'r', encoding='utf-8') as f:
    candidates = json.load(f)

# 筛选本科学历的候选人
bachelor_candidates = [c for c in candidates if c.get('education') == '本科']
print(f"本科学历候选人: {len(bachelor_candidates)} 人")

# 筛选离职-随时到岗的候选人
available_candidates = [c for c in candidates if c.get('jobStatus') == '离职-随时到岗']
print(f"随时到岗候选人: {len(available_candidates)} 人")

# 筛选期望薪资在5-10K的候选人
salary_range_candidates = [c for c in candidates if '5' in c.get('salary', '') or '6' in c.get('salary', '')]
print(f"期望薪资5-10K候选人: {len(salary_range_candidates)} 人")

# 获取所有刚刚活跃的候选人
active_candidates = [c for c in candidates if c.get('activity') == '刚刚活跃']
print(f"刚刚活跃候选人: {len(active_candidates)} 人")
```

## 🔧 技术实现

### 核心技术

- **Playwright**: 浏览器自动化
- **JavaScript 注入**: 在浏览器中执行 JS 提取数据
- **正则表达式**: 解析候选人信息
- **异步编程**: 高效处理网络请求

### 数据提取流程

```mermaid
graph LR
    A[启动浏览器] --> B[加载登录状态]
    B --> C[导航到推荐页面]
    C --> D[查找 recommendFrame]
    D --> E[获取候选人卡片]
    E --> F[滚动加载更多]
    F --> G[提取每个卡片信息]
    G --> H[保存为JSON]
    H --> I[生成统计报告]
```

### 关键选择器

```python
# iframe
frame.name == 'recommendFrame'

# 候选人卡片列表
'ul.card-list > li'

# 单个卡片
'ul.card-list > li:nth-child(N)'
```

## 📈 数据统计示例

运行脚本后的统计结果示例：

```
📊 共获取 60 个候选人信息

📈 数据统计
================================================================================
学历分布:
  本科: 35 人
  大专: 21 人
  中专/中技: 2 人
  硕士: 1 人
  博士: 1 人

求职状态分布:
  离职-随时到岗: 37 人
  None: 11 人
  在职-月内到岗: 7 人
  在职-考虑机会: 3 人
  在职-暂不考虑: 2 人
```

## ⚠️ 注意事项

### 1. 登录状态

- ✅ 必须先登录 Boss直聘
- ✅ 登录状态保存在 `boss_auth.json` 文件中
- ⚠️ 如果登录过期，需要重新登录

### 2. 滚动加载

- ✅ 每次滚动会等待 2 秒加载数据
- ✅ 滚动轮数越多，获取的候选人越多
- ⚠️ 但页面也可能有加载限制

### 3. 数据准确性

- ✅ 大部分字段能准确提取
- ⚠️ 部分字段可能为 `None`（取决于卡片内容）
- ⚠️ `expectedPosition` 字段可能包含额外信息（如优势描述）

### 4. 性能

- ✅ 平均每个候选人提取时间: ~0.1 秒
- ✅ 60个候选人总耗时: ~10 秒
- ⚠️ 滚动加载会增加总时间

## 🐛 常见问题

### Q1: 提示 "未找到 recommendFrame"

**原因**: 未登录或页面未加载完成

**解决方案**:
- 检查 `boss_auth.json` 文件是否存在
- 增加等待时间 `await asyncio.sleep(5)`

### Q2: 提取的候选人数量为 0

**原因**: 选择器不匹配或页面结构变化

**解决方案**:
- 检查选择器 `ul.card-list > li` 是否正确
- 查看浏览器控制台是否有错误

### Q3: 部分字段提取失败

**原因**: 正则表达式不匹配或字段不存在

**解决方案**:
- 检查 `fullText` 字段的完整文本
- 调整正则表达式匹配规则

### Q4: 滚动加载没有新增候选人

**原因**: 已经加载到底部或网络延迟

**解决方案**:
- 增加等待时间 `await asyncio.sleep(3)`
- 减少滚动轮数

## 📚 相关文档

- [候选人列表结构分析文档](./CANDIDATE_LIST_STRUCTURE.md)
- [候选人列表探索测试脚本](./test_candidate_list_explorer.py)
- [Boss直聘自动化项目](../README.md)

## 🔄 版本历史

- **v1.0** (2025-10-29): 初始版本
  - 基本的候选人信息提取
  - 滚动加载支持
  - JSON 数据导出
  - 统计分析功能

## 📝 许可证

本脚本仅用于学习和研究目的，请勿用于商业用途。

---

**作者**: Claude Code + Boss直聘自动化项目
**最后更新**: 2025-10-29
