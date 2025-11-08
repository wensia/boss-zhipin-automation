# 筛选功能集成指南

本指南说明如何将完整的筛选功能集成到自动化向导中。

---

## 📁 已创建的文件

### 前端

1. **`frontend/src/types/filters.ts`** - 筛选条件类型定义
   - `FilterOptions` 接口
   - `FILTER_CONFIG` 配置
   - `DEFAULT_FILTERS` 默认值

2. **`frontend/src/components/FilterConfig.tsx`** - 筛选配置组件
   - 完整的UI组件
   - 包含所有13类筛选条件
   - 年龄、专业、活跃度、性别等

### 后端

1. **`backend/app/models/filters.py`** - 筛选条件数据模型
   - Pydantic模型定义
   - 字段验证

2. **`backend/app/utils/filters_applier.py`** - 筛选条件应用器
   - `FiltersApplier` 类
   - `apply_all_filters()` 方法
   - 单选、多选、关键词等各种类型的处理

---

## 🔧 集成步骤

### 第1步：修改 `automation-wizard.tsx`

#### 1.1 导入依赖

在文件顶部添加：

```typescript
import { FilterConfig } from "@/components/FilterConfig";
import { FilterOptions, DEFAULT_FILTERS } from "@/types/filters";
```

#### 1.2 添加状态管理

在组件的 state 部分添加：

```typescript
// 在现有的 useState 后添加
const [filters, setFilters] = useState<FilterOptions>(DEFAULT_FILTERS);
```

#### 1.3 修改步骤4的渲染函数

找到 `renderConfigureStep()` 函数，修改为：

```typescript
const renderConfigureStep = () => {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-6 w-6 text-primary" />
            步骤 4: 配置筛选条件
          </CardTitle>
          <CardDescription>
            配置候选人筛选条件，将在浏览器中自动应用
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* 每个职位打招呼数量 */}
          <div className="space-y-2">
            <Label htmlFor="maxContacts">每个职位打招呼数量</Label>
            <Input
              id="maxContacts"
              type="number"
              min="1"
              max="100"
              value={maxContacts}
              onChange={(e) => setMaxContacts(parseInt(e.target.value) || 10)}
              className="max-w-xs"
            />
            <p className="text-sm text-muted-foreground">
              建议每个职位不超过 50 人，避免触发平台限制
            </p>
          </div>

          <Separator />

          {/* 筛选条件配置 */}
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold">候选人筛选条件</h3>
              <p className="text-sm text-muted-foreground">
                设置筛选条件以精准匹配目标候选人
              </p>
            </div>

            <FilterConfig filters={filters} onChange={setFilters} />
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
```

#### 1.4 修改步骤5（确认步骤）

在 `renderConfirmStep()` 中添加筛选条件的显示：

```typescript
const renderConfirmStep = () => {
  // 统计设置的筛选条件数量
  const activeFiltersCount = Object.entries(filters).filter(([key, value]) => {
    if (key === 'age') return value !== null;
    if (Array.isArray(value)) return value.length > 0;
    return value && value !== '不限';
  }).length;

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <PlayCircle className="h-6 w-6 text-primary" />
            步骤 5: 确认并启动
          </CardTitle>
          <CardDescription>
            请确认以下配置无误后，点击启动按钮
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <div>
              <Label className="text-muted-foreground">浏览器显示</Label>
              <p className="font-medium">
                {showBrowser ? '显示窗口' : '后台运行（隐藏窗口）'}
              </p>
            </div>

            <div>
              <Label className="text-muted-foreground">每个职位打招呼数量</Label>
              <p className="font-medium">{maxContacts} 人</p>
            </div>

            <div>
              <Label className="text-muted-foreground">筛选条件</Label>
              <p className="font-medium">
                已设置 {activeFiltersCount} 项筛选条件
              </p>

              {/* 显示部分关键筛选 */}
              {filters.age && (
                <p className="text-sm text-muted-foreground">
                  • 年龄: {filters.age.min} - {filters.age.max || '不限'} 岁
                </p>
              )}
              {filters.gender && filters.gender !== '不限' && (
                <p className="text-sm text-muted-foreground">
                  • 性别: {filters.gender}
                </p>
              )}
              {filters.experience && filters.experience !== '不限' && (
                <p className="text-sm text-muted-foreground">
                  • 经验: {filters.experience}
                </p>
              )}
              {filters.education && filters.education !== '不限' && (
                <p className="text-sm text-muted-foreground">
                  • 学历: {filters.education}
                </p>
              )}
            </div>

            <div className="pt-4 border-t">
              <Label className="text-muted-foreground">预计操作</Label>
              <p className="font-medium">
                将应用筛选条件并自动向推荐的候选人发送问候
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
```

#### 1.5 修改启动逻辑

在 `handleStart()` 函数中，将筛选条件传递给后端：

```typescript
const handleStart = async () => {
  setIsStarting(true);

  try {
    const response = await fetch('/api/automation/start', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        show_browser: showBrowser,
        max_contacts: maxContacts,
        filters: filters,  // 添加筛选条件
      }),
    });

    // ... 其余代码保持不变
  } catch (error) {
    // ... 错误处理
  } finally {
    setIsStarting(false);
  }
};
```

---

### 第2步：创建后端API端点

在 `backend/app/routes/automation.py` 中：

#### 2.1 导入依赖

```python
from app.models.filters import FilterOptions
from app.utils.filters_applier import FiltersApplier
```

#### 2.2 修改启动请求模型

```python
from pydantic import BaseModel, Field
from typing import Optional

class StartAutomationRequest(BaseModel):
    show_browser: bool = Field(False, description="是否显示浏览器窗口")
    max_contacts: int = Field(10, ge=1, le=100, description="每个职位打招呼的最大数量")
    filters: Optional[FilterOptions] = Field(None, description="筛选条件")
```

#### 2.3 修改启动端点

```python
@router.post("/start")
async def start_automation(request: StartAutomationRequest):
    """启动自动化任务"""
    global automation_instance

    try:
        # 初始化自动化实例
        automation = BossAutomation()
        await automation.initialize(headless=not request.show_browser)

        # 检查登录状态
        login_status = await automation.check_login_status()
        if not login_status.get('logged_in'):
            return {
                "success": False,
                "error": "未登录，请先登录Boss直聘"
            }

        # 导航到推荐页面
        await automation.navigate_to_recommend_page()
        await asyncio.sleep(3)

        # 获取iframe
        recommend_frame = None
        for frame in automation.page.frames:
            if frame.name == 'recommendFrame':
                recommend_frame = frame
                break

        if not recommend_frame:
            return {
                "success": False,
                "error": "未找到推荐页面iframe"
            }

        # 应用筛选条件
        if request.filters:
            logger.info("应用筛选条件...")
            applier = FiltersApplier(recommend_frame, automation.page)

            # 打开筛选面板
            if not await applier.open_filter_panel():
                return {
                    "success": False,
                    "error": "无法打开筛选面板"
                }

            # 应用所有筛选条件
            filter_result = await applier.apply_all_filters(request.filters)

            if not filter_result['success']:
                return {
                    "success": False,
                    "error": "筛选条件应用失败",
                    "details": filter_result
                }

            logger.info(f"✅ 筛选条件应用完成: {len(filter_result['applied_filters'])} 项")

        # 保存实例
        automation_instance = automation

        # 开始自动化任务...
        # （这里继续原有的打招呼逻辑）

        return {
            "success": True,
            "message": "自动化任务已启动",
            "filters_applied": len(filter_result.get('applied_filters', [])) if request.filters else 0
        }

    except Exception as e:
        logger.exception(f"启动自动化失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

---

## 🧪 测试步骤

### 测试1：前端UI测试

1. 启动前端：`npm run dev`
2. 访问自动化向导
3. 进入步骤4，验证筛选条件UI是否正确显示
4. 测试各种筛选条件的选择和取消
5. 检查步骤5是否正确显示已选筛选条件

### 测试2：后端应用测试

创建测试脚本 `test_filters_integration.py`：

```python
import asyncio
from app.services.boss_automation import BossAutomation
from app.models.filters import FilterOptions, AgeFilter
from app.utils.filters_applier import FiltersApplier

async def test_filters():
    automation = BossAutomation()

    try:
        await automation.initialize(headless=False)

        # 登录并导航
        login_status = await automation.check_login_status()
        if not login_status.get('logged_in'):
            print("请先登录")
            return

        await automation.navigate_to_recommend_page()
        await asyncio.sleep(3)

        # 获取frame
        recommend_frame = None
        for frame in automation.page.frames:
            if frame.name == 'recommendFrame':
                recommend_frame = frame
                break

        if not recommend_frame:
            print("未找到iframe")
            return

        # 创建测试筛选条件
        filters = FilterOptions(
            age=AgeFilter(min=25, max=40),
            gender="男",
            experience="3-5年",
            education="本科",
            activity="今日活跃"
        )

        # 应用筛选
        applier = FiltersApplier(recommend_frame, automation.page)
        await applier.open_filter_panel()
        result = await applier.apply_all_filters(filters)

        print(f"应用结果: {result}")

        # 保持浏览器打开
        await asyncio.sleep(300)

    finally:
        await automation.cleanup()

if __name__ == "__main__":
    asyncio.run(test_filters())
```

运行测试：
```bash
cd backend
source .venv/bin/activate
python test_filters_integration.py
```

---

## ✅ 验证清单

- [ ] 前端UI正确显示所有13类筛选条件
- [ ] 单选按钮正常工作
- [ ] 多选按钮正常工作
- [ ] 年龄滑块正确配置
- [ ] 关键词添加/删除功能正常
- [ ] 步骤5正确显示已配置的筛选条件
- [ ] 后端正确接收筛选条件数据
- [ ] 筛选面板成功打开
- [ ] 所有筛选条件成功应用
- [ ] 确定按钮成功点击
- [ ] 筛选条件生效（候选人列表更新）

---

## 📝 注意事项

1. **筛选条件的顺序**: 建议先设置年龄等基础条件，最后设置关键词

2. **"不限"的处理**:
   - 前端：空数组或null表示不限
   - 后端：跳过该筛选条件

3. **错误处理**:
   - 如果某个筛选条件应用失败，继续应用其他条件
   - 在最终结果中报告失败的筛选项

4. **性能优化**:
   - 筛选条件之间添加适当的延迟（0.3-0.5秒）
   - 避免过快操作导致UI未响应

5. **兼容性**:
   - Boss直聘可能更新UI，筛选器选择器可能需要调整
   - 建议定期测试和维护

---

## 🚀 下一步优化

1. **筛选模板**:
   - 允许用户保存常用筛选配置
   - 提供预设模板（如"应届生"、"高级人才"等）

2. **智能推荐**:
   - 根据职位描述自动推荐筛选条件

3. **筛选效果预览**:
   - 在确认前显示预计匹配的候选人数量

4. **批量配置**:
   - 为不同职位配置不同的筛选条件

---

## 📞 技术支持

如有问题，请参考：
- `AGE_SLIDER_SOLUTION_FOUND.md` - 年龄滑块实现详情
- `AGE_SLIDER_MCP_FINAL_REPORT.md` - 完整测试报告
- `frontend/src/components/FilterConfig.tsx` - 前端组件源码
- `backend/app/utils/filters_applier.py` - 后端应用逻辑

---

**集成完成后，自动化向导将拥有完整的筛选功能！** 🎉
