# Boss直聘候选人数据提取工具 - 项目总结

## 📋 项目概述

本项目提供了一套完整的工具链，用于从 Boss直聘 推荐候选人页面自动获取候选人信息，并进行数据分析。

## 🎯 核心功能

### 1. 候选人列表结构探索 ✅

**脚本**: `test_candidate_list_explorer.py`

- ✅ 探索 Boss直聘 页面的 DOM 结构
- ✅ 定位 iframe 和候选人卡片元素
- ✅ 测试点击和滚动交互
- ✅ 生成详细的结构文档

**关键发现**:
- iframe 名称: `recommendFrame`
- 候选人卡片选择器: `ul.card-list > li` (类名: `card-item`)
- 滚动方式: 在 iframe 的 window 中滚动
- 点击行为: 打开详情面板，无页面跳转

### 2. 候选人信息自动提取 ✅

**脚本**: `get_candidates_info.py`

- ✅ 自动登录（使用保存的登录状态）
- ✅ 自动滚动加载更多候选人
- ✅ 智能提取 15+ 个数据字段
- ✅ 保存为 JSON 格式
- ✅ 实时显示进度和统计

**提取字段**:
| 字段 | 说明 | 示例 |
|------|------|------|
| name | 姓名 | "李嘉昕" |
| age | 年龄 | 28 |
| experience | 工作经验 | "3年" / "25年应届生" |
| education | 学历 | "本科" / "硕士" |
| salary | 期望薪资 | "4-9K" |
| jobStatus | 求职状态 | "离职-随时到岗" |
| expectedCity | 期望城市 | "天津" |
| expectedPosition | 期望职位 | "新媒体运营" |
| advantage | 个人优势 | 候选人优势描述 |
| activity | 活跃度 | "刚刚活跃" |
| workStartDate | 工作起始日期 | "2024.09" |
| workEndDate | 工作结束日期 | "2025.05" |
| fullText | 完整文本 | 卡片完整内容 |
| selector | CSS选择器 | 元素定位器 |

### 3. 数据分析工具 ✅

**脚本**: `analyze_candidates.py`

- ✅ 学历分布统计
- ✅ 期望薪资分布统计
- ✅ 求职状态分析
- ✅ 活跃度分析
- ✅ 年龄分布统计
- ✅ 多条件筛选
- ✅ 综合查询示例

## 📊 测试结果

### 测试环境
- 日期: 2025-10-29
- 浏览器: Chromium (Playwright)
- 测试页面: https://www.zhipin.com/web/chat/recommend

### 数据统计（60个候选人样本）

**学历分布**:
- 本科: 35 人 (58.3%)
- 大专: 21 人 (35.0%)
- 中专/中技: 2 人 (3.3%)
- 硕士: 1 人 (1.7%)
- 博士: 1 人 (1.7%)

**求职状态分布**:
- 离职-随时到岗: 37 人 (61.7%)
- 在职-月内到岗: 7 人 (11.7%)
- 在职-考虑机会: 3 人 (5.0%)
- 在职-暂不考虑: 2 人 (3.3%)
- 未知: 11 人 (18.3%)

**活跃度分布**:
- 刚刚活跃: 41 人 (68.3%)
- 今日活跃: 3 人 (5.0%)
- 未知: 16 人 (26.7%)

**年龄分布**:
- 平均年龄: 28.2 岁
- 年龄范围: 20 - 45 岁
- 20-25岁: 29 人 (48.3%)
- 26-30岁: 15 人 (25.0%)
- 31-35岁: 7 人 (11.7%)

### 性能指标

- **初始加载**: 15 个候选人
- **滚动3轮后**: 60 个候选人
- **新增候选人**: 45 个
- **平均提取速度**: ~0.1 秒/人
- **总耗时**: ~10 秒（60人）

## 📁 项目文件

### 核心脚本

| 文件 | 说明 | 状态 |
|------|------|------|
| `test_candidate_list_explorer.py` | 候选人列表结构探索 | ✅ 完成 |
| `get_candidates_info.py` | 候选人信息提取工具 | ✅ 完成 |
| `analyze_candidates.py` | 数据分析示例脚本 | ✅ 完成 |

### 文档

| 文件 | 说明 | 状态 |
|------|------|------|
| `CANDIDATE_LIST_STRUCTURE.md` | 候选人列表结构详细文档 | ✅ 完成 |
| `GET_CANDIDATES_INFO_README.md` | 信息提取工具使用指南 | ✅ 完成 |
| `CANDIDATE_DATA_EXTRACTION_SUMMARY.md` | 项目总结（本文档） | ✅ 完成 |

### 数据文件

| 文件 | 说明 | 示例 |
|------|------|------|
| `candidates_data.json` | 候选人信息JSON数据 | 163KB (60人) |
| `candidate_list_exploration_output.log` | 探索脚本日志 | 自动生成 |
| `boss_auth.json` | Boss直聘登录状态 | 需要保密 |

## 🚀 快速开始

### 1. 探索页面结构（可选）

```bash
uv run python test_candidate_list_explorer.py
```

这会打开浏览器，自动探索候选人列表的结构。

### 2. 获取候选人信息

```bash
uv run python get_candidates_info.py
```

这会：
- 自动登录（使用已保存的登录状态）
- 导航到推荐牛人页面
- 滚动加载候选人
- 提取所有信息并保存为 `candidates_data.json`

### 3. 分析数据

```bash
uv run python analyze_candidates.py
```

这会：
- 加载 `candidates_data.json`
- 生成统计报告
- 展示筛选示例
- 显示候选人详情

## 💡 使用示例

### 示例 1: 获取前20个候选人

```python
# 修改 get_candidates_info.py 中的配置
MAX_CANDIDATES = 20
SCROLL_ROUNDS = 0

# 运行脚本
uv run python get_candidates_info.py
```

### 示例 2: 筛选符合条件的候选人

```python
import json

# 加载数据
with open('candidates_data.json', 'r', encoding='utf-8') as f:
    candidates = json.load(f)

# 筛选条件: 本科 + 离职随时到岗 + 刚刚活跃
filtered = [c for c in candidates
            if c.get('education') == '本科'
            and c.get('jobStatus') == '离职-随时到岗'
            and c.get('activity') == '刚刚活跃']

print(f"符合条件的候选人: {len(filtered)} 人")
for c in filtered:
    print(f"- {c['name']}, {c['age']}岁, {c['salary']}")
```

### 示例 3: 导出为 Excel

```python
import json
import pandas as pd

# 加载数据
with open('candidates_data.json', 'r', encoding='utf-8') as f:
    candidates = json.load(f)

# 转换为 DataFrame
df = pd.DataFrame(candidates)

# 选择关键字段
df_export = df[['name', 'age', 'education', 'experience', 'salary', 'jobStatus', 'activity']]

# 导出为 Excel
df_export.to_excel('candidates.xlsx', index=False)
print("✅ 已导出到 candidates.xlsx")
```

## 🔧 技术实现

### 核心技术栈

- **Playwright**: 浏览器自动化
- **Python 3.9+**: 编程语言
- **Asyncio**: 异步编程
- **正则表达式**: 数据解析
- **JSON**: 数据存储

### 关键技术点

1. **iframe 访问**
   ```python
   recommend_frame = None
   for frame in page.frames:
       if frame.name == 'recommendFrame':
           recommend_frame = frame
   ```

2. **滚动加载**
   ```python
   await recommend_frame.evaluate("""
       window.scrollTo({
           top: document.documentElement.scrollHeight,
           behavior: 'smooth'
       });
   """)
   ```

3. **数据提取**
   ```python
   info = await card.evaluate(r"""
       (el) => {
           const text = el.textContent;
           // 使用正则表达式提取字段
           const nameMatch = text.match(/\d+K?\s+([^\s]+)/);
           return { name: nameMatch ? nameMatch[1] : null };
       }
   """)
   ```

## ⚠️ 注意事项

### 1. 登录状态

- ✅ 必须先登录 Boss直聘
- ✅ 登录状态保存在 `boss_auth.json`
- ⚠️ 定期检查登录状态是否过期

### 2. 反爬虫

- ✅ 使用了反检测脚本
- ✅ 模拟真实浏览器行为
- ⚠️ 建议适当延迟请求

### 3. 数据准确性

- ✅ 大部分字段提取准确
- ⚠️ 部分字段可能为空或格式不一致
- ⚠️ 建议做数据清洗和验证

### 4. 法律合规

- ⚠️ 仅用于个人学习和研究
- ⚠️ 不得用于商业目的
- ⚠️ 遵守 Boss直聘 服务条款

## 🐛 已知问题

### 1. 期望职位字段不准确

**问题**: `expectedPosition` 字段可能包含完整的"优势"描述

**原因**: 正则表达式匹配范围过大

**解决方案**: 调整正则表达式，只匹配职位名称部分

### 2. 部分候选人信息为空

**问题**: 某些字段（如 `activity`, `jobStatus`）为 `None`

**原因**: 卡片中没有显示该信息

**解决方案**: 这是正常现象，使用时需要处理空值

### 3. 滚动加载可能不稳定

**问题**: 有时滚动后没有加载新候选人

**原因**: 网络延迟或已加载到底部

**解决方案**: 增加等待时间或减少滚动轮数

## 🔮 未来改进

### 短期计划

- [ ] 优化字段提取准确性
- [ ] 添加错误重试机制
- [ ] 支持导出为 Excel/CSV
- [ ] 添加更多筛选条件

### 长期计划

- [ ] 集成到主自动化系统
- [ ] 支持批量职位筛选
- [ ] 添加候选人跟踪功能
- [ ] 实现自动打招呼

## 📚 相关文档

- [候选人列表结构分析](./CANDIDATE_LIST_STRUCTURE.md)
- [信息提取工具使用指南](./GET_CANDIDATES_INFO_README.md)
- [Boss直聘自动化项目主文档](../README.md)

## 👥 贡献者

- Claude Code
- Boss直聘自动化项目团队

## 📝 版本历史

- **v1.0** (2025-10-29): 初始版本
  - 候选人列表结构探索
  - 信息提取工具
  - 数据分析示例
  - 完整文档

## 📄 许可证

本项目仅用于学习和研究目的，请勿用于商业用途。

---

**最后更新**: 2025-10-29
**项目状态**: ✅ 完成
