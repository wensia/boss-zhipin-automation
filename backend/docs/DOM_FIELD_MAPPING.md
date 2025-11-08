# Boss直聘候选人卡片 DOM 字段映射详细分析

## 📋 概述

基于提供的HTML结构和截图，详细分析每个字段的DOM结构和提取方法。

## 🔍 完整DOM结构分析

```html
<li class="card-item">
  <div class="candidate-card-wrap">
    <div class="card-inner" data-geekid="候选人ID">

      <!-- 第一列：头像、性别、薪资 -->
      <div class="col-1">
        <div class="avatar-wrap">
          <img src="头像URL" alt="吴丹丹" class="avatar">
          <i class="gender iboss-icon_women"></i>  <!-- 性别：icon_women=女, icon_men=男 -->
        </div>
        <span class="salary-wrap">4-6K</span>  <!-- 期望薪资 -->
      </div>

      <!-- 第二列：主要信息 -->
      <div class="col-2">
        <!-- 姓名 -->
        <div class="row name-wrap">
          <span class="name">吴丹丹</span>
          <img class="online-marker" ...>  <!-- 在线状态 -->
        </div>

        <!-- 基础信息：年龄·经验·学历·求职状态 -->
        <div class="row">
          <div class="base-info join-text-wrap">
            30岁<i class="join-shape line"></i>
            10年<i class="join-shape line"></i>
            本科<i class="join-shape line"></i>
            离职-随时到岗<i class="join-shape line"></i>
          </div>
        </div>

        <!-- 期望信息 -->
        <div class="row row-flex">
          <span class="label">期望：</span>
          <span class="content">
            <div class="join-text-wrap">
              天津<i class="join-shape dot"></i>
              新媒体运营<i class="join-shape dot"></i>
            </div>
          </span>
        </div>

        <!-- 优势描述 -->
        <div class="row row-flex geek-desc">
          <span class="label">优势：</span>
          <span class="content">性格开朗，热情活泼...</span>
        </div>

        <!-- 技能标签 -->
        <div class="row tags">
          <div class="tags-wrap">
            <span class="tag-item">电商直播运营</span>
            <span class="tag-item">监控</span>
            <span class="tag-item">面试</span>
            <span class="tag-item">短视频</span>
            <span class="tag-item">热点话题</span>
          </div>
        </div>
      </div>

      <!-- 第三列：时间线 -->
      <div class="col-3">
        <!-- 工作经历 -->
        <div class="timeline-wrap work-exps">
          <div class="timeline-item">
            <div class="time join-text-wrap">
              2023.06<i class="join-shape minus"></i>2025.10<i class="join-shape minus"></i>
            </div>
            <div class="content join-text-wrap">
              海之界海水生物检疫工作室<i class="join-shape dot"></i>
              运营助理/专员<i class="join-shape dot"></i>
            </div>
          </div>
          <div class="timeline-item">...</div>
        </div>

        <!-- 教育经历 -->
        <div class="timeline-wrap edu-exps">
          <div class="timeline-item">
            <div class="time join-text-wrap">
              2015<i class="join-shape minus"></i>2017<i class="join-shape minus"></i>
            </div>
            <div class="content join-text-wrap">
              天津工业大学<i class="join-shape dot"></i>
              工商企业管理<i class="join-shape dot"></i>
              本科<i class="join-shape dot"></i>
            </div>
          </div>
          <div class="timeline-item">...</div>
        </div>
      </div>

    </div>
  </div>
</li>
```

## 📊 字段映射表

### 第一列（col-1）

| 字段名 | DOM选择器 | 提取方法 | 示例值 | 说明 |
|--------|----------|----------|--------|------|
| avatarUrl | `.col-1 .avatar-wrap img` | `getAttribute('src')` | "https://img.bosszhipin.com/..." | 头像URL |
| gender | `.col-1 .gender` | 根据class判断 | "女" / "男" | `icon_women`=女, `icon_men`=男 |
| salary | `.col-1 .salary-wrap` | `textContent` | "4-6K" | 期望薪资 |

### 第二列（col-2）

| 字段名 | DOM选择器 | 提取方法 | 示例值 | 说明 |
|--------|----------|----------|--------|------|
| name | `.col-2 .name` | `textContent` | "吴丹丹" | 姓名 |
| isOnline | `.col-2 .online-marker` | 元素是否存在 | true/false | 是否在线 |

#### 基础信息（base-info）

使用 `<i class="join-shape line">` 分隔的字段：

| 字段名 | 提取方法 | 示例值 | 说明 |
|--------|----------|--------|------|
| age | 正则匹配 `(\d+)岁` | 30 | 年龄 |
| experience | 正则匹配 | "10年" / "25年应届生" | 工作经验 |
| education | 枚举匹配 | "本科" | 学历 |
| jobStatus | 枚举匹配 | "离职-随时到岗" | 求职状态 |

**注意**: 这些字段用 `<i class="join-shape line">` 分隔，但在 `textContent` 中显示不出来。

#### 期望信息（row-flex）

使用 `<i class="join-shape dot">` 分隔的字段：

| 字段名 | 提取方法 | 示例值 | 说明 |
|--------|----------|--------|------|
| expectedCity | 第一个文本节点 | "天津" | 期望城市 |
| expectedPosition | 第二个文本节点 | "新媒体运营" | 期望职位 |

#### 其他字段

| 字段名 | DOM选择器 | 提取方法 | 示例值 |
|--------|----------|----------|--------|
| advantage | `.geek-desc .content` | `textContent` | "性格开朗..." |
| tags | `.tags-wrap .tag-item` | 遍历所有元素 | ["电商直播运营", "监控", ...] |

### 第三列（col-3）

#### 工作经历（work-exps）

每个 `.timeline-item` 包含：

| 字段名 | DOM选择器 | 提取方法 | 示例值 | 说明 |
|--------|----------|----------|--------|------|
| 时间 | `.time.join-text-wrap` | 解析子元素 | - | 用 `<i class="join-shape minus">` 分隔 |
| startDate | 第一个文本节点 | 直接读取 | "2023.06" | 开始时间 |
| endDate | 第二个文本节点 | 直接读取 | "2025.10" | 结束时间（可能是"至今"） |
| 内容 | `.content.join-text-wrap` | 解析子元素 | - | 用 `<i class="join-shape dot">` 分隔 |
| company | 第一个文本节点 | 直接读取 | "海之界海水生物检疫工作室" | 公司名称 |
| position | 第二个文本节点 | 直接读取 | "运营助理/专员" | 职位名称 |

#### 教育经历（edu-exps）

每个 `.timeline-item` 包含：

| 字段名 | DOM选择器 | 提取方法 | 示例值 | 说明 |
|--------|----------|----------|--------|------|
| 时间 | `.time.join-text-wrap` | 解析子元素 | - | 用 `<i class="join-shape minus">` 分隔 |
| startDate | 第一个文本节点 | 直接读取 | "2015" | 入学年份 |
| endDate | 第二个文本节点 | 直接读取 | "2017" | 毕业年份 |
| 内容 | `.content.join-text-wrap` | 解析子元素 | - | 用 `<i class="join-shape dot">` 分隔 |
| school | 第一个文本节点 | 直接读取 | "天津工业大学" | 学校名称 |
| major | 第二个文本节点 | 直接读取 | "工商企业管理" | 专业 |
| degree | 第三个文本节点 | 直接读取 | "本科" | 学历 |

## 🔧 关键技术点

### 1. join-shape 分隔符

Boss直聘使用了自定义的分隔符样式，而不是普通的文本字符：

- `<i class="join-shape line">` - 用于分隔基础信息（年龄、经验、学历、求职状态）
- `<i class="join-shape dot">` - 用于分隔期望信息、工作内容、教育内容
- `<i class="join-shape minus">` - 用于分隔时间范围

这些分隔符在 `textContent` 中**不会显示**，因此：

❌ **错误方法**:
```javascript
const text = element.textContent; // "天津新媒体运营"
const parts = text.split('·'); // 无法分割，因为没有·字符
```

✅ **正确方法**:
```javascript
// 方法1: 遍历子节点
const childNodes = element.childNodes;
const parts = [];
childNodes.forEach(node => {
  if (node.nodeType === Node.TEXT_NODE) {
    parts.push(node.textContent.trim());
  }
});

// 方法2: 用分隔符替换后分割
const html = element.innerHTML;
const text = html.replace(/<i[^>]*class="join-shape[^>]*><\/i>/g, '|');
const tempDiv = document.createElement('div');
tempDiv.innerHTML = text;
const parts = tempDiv.textContent.split('|').map(s => s.trim()).filter(s => s);
```

### 2. 数据提取策略

**推荐策略**：遍历子节点，按文本节点顺序提取

```javascript
function extractJoinTextParts(element) {
  const parts = [];
  for (const child of element.childNodes) {
    if (child.nodeType === Node.TEXT_NODE && child.textContent.trim()) {
      parts.push(child.textContent.trim());
    }
  }
  return parts;
}

// 使用示例
const expectEl = document.querySelector('.row-flex .content .join-text-wrap');
const parts = extractJoinTextParts(expectEl);
// parts = ["天津", "新媒体运营"]
```

### 3. 完整提取函数示例

```javascript
function extractWorkExperience(timelineItem) {
  // 提取时间
  const timeEl = timelineItem.querySelector('.time');
  const timeParts = extractJoinTextParts(timeEl);

  // 提取内容
  const contentEl = timelineItem.querySelector('.content');
  const contentParts = extractJoinTextParts(contentEl);

  return {
    startDate: timeParts[0] || null,
    endDate: timeParts[1] || '至今',
    company: contentParts[0] || null,
    position: contentParts[1] || null
  };
}

function extractEducationExperience(timelineItem) {
  // 提取时间
  const timeEl = timelineItem.querySelector('.time');
  const timeParts = extractJoinTextParts(timeEl);

  // 提取内容
  const contentEl = timelineItem.querySelector('.content');
  const contentParts = extractJoinTextParts(contentEl);

  return {
    startDate: timeParts[0] || null,
    endDate: timeParts[1] || null,
    school: contentParts[0] || null,
    major: contentParts[1] || null,
    degree: contentParts[2] || null
  };
}
```

## 📝 数据验证规则

### 必填字段

- ✅ `name` - 姓名（必须有值）
- ✅ `age` - 年龄（必须有值且在16-60之间）
- ✅ `education` - 学历（必须有值）
- ✅ `salary` - 期望薪资（必须有值）

### 可选字段

- ⭕ `gender` - 性别（部分候选人没有显示）
- ⭕ `jobStatus` - 求职状态（部分候选人没有显示）
- ⭕ `expectedPosition` - 期望职位（大部分应该有）

### 数组字段

- 📋 `tags` - 技能标签（可能为空数组）
- 📋 `workExperiences` - 工作经历（至少1条）
- 📋 `educationExperiences` - 教育经历（至少1条）

## ⚠️ 常见问题

### Q1: textContent获取不到分隔符？

**原因**: Boss直聘使用`<i class="join-shape">`标签作为视觉分隔符，textContent会忽略这些标签。

**解决**: 遍历子节点或使用innerHTML替换

### Q2: 期望职位总是为空？

**原因**: "天津新媒体运营"被合并到expectedCity字段了。

**解决**: 正确解析join-text-wrap的子节点

### Q3: 工作经历的公司和职位合并？

**原因**: 分割逻辑不正确，使用了split('·')但实际没有这个字符。

**解决**: 使用extractJoinTextParts函数提取

### Q4: 时间格式不正确？

**原因**: "2024.10-2025.05"被解析为"2024.102025.05"。

**解决**: 正确分离子节点中的文本

## 🎯 最终数据格式

```json
{
  "geekId": "d5ae04fb9f0128ea1HV82t27FVo~",
  "avatarUrl": "https://...",
  "gender": "女",
  "salary": "4-6K",
  "name": "吴丹丹",
  "isOnline": true,
  "age": 30,
  "experience": "10年",
  "education": "本科",
  "jobStatus": "离职-随时到岗",
  "expectedCity": "天津",
  "expectedPosition": "新媒体运营",
  "advantage": "性格开朗，热情活泼...",
  "tags": ["电商直播运营", "监控", "面试", "短视频", "热点话题"],
  "workExperiences": [
    {
      "startDate": "2023.06",
      "endDate": "2025.10",
      "company": "海之界海水生物检疫工作室",
      "position": "运营助理/专员"
    },
    {
      "startDate": "2019.07",
      "endDate": "2020.10",
      "company": "豪利时商贸",
      "position": "淘宝运营"
    }
  ],
  "educationExperiences": [
    {
      "startDate": "2015",
      "endDate": "2017",
      "school": "天津工业大学",
      "major": "工商企业管理",
      "degree": "本科"
    },
    {
      "startDate": "2013",
      "endDate": "2016",
      "school": "天津滨海职业学院",
      "major": "国际金融",
      "degree": "大专"
    }
  ]
}
```

## 📚 参考资料

- [Boss直聘候选人列表结构文档](./CANDIDATE_LIST_STRUCTURE.md)
- [精确提取脚本](./get_candidates_info_precise.py)

---

**作者**: Claude Code
**最后更新**: 2025-10-29
**版本**: v1.0
