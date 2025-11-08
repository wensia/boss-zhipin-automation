# 🚀 Boss直聘自动打招呼 - 快速开始

## 一分钟快速使用

### 步骤1：确认登录状态
```bash
# 确保有有效的登录文件
ls boss_auth.json  # 应该存在
```

### 步骤2：运行测试（10个候选人）
```bash
cd backend
uv run python test_auto_greeting.py
```

### 步骤3：查看结果
```
✅ 成功处理: 10/10
成功率: 100.0%
```

完成！🎉

---

## Python代码集成

### 最简单的用法

```python
from auto_greeting_reusable import auto_greet_candidates
import asyncio

async def main():
    result = await auto_greet_candidates(target_count=20)
    print(f"成功: {result['success_count']}/{result['total']}")

asyncio.run(main())
```

### 高级用法（分批处理）

```python
from auto_greeting_reusable import GreetingAutomation
import asyncio

async def main():
    async with GreetingAutomation() as automation:
        await automation.initialize()

        # 第一批：10个
        result1 = await automation.greet_multiple(target_count=10)

        # 休息1分钟
        await asyncio.sleep(60)

        # 第二批：10个
        result2 = await automation.greet_multiple(target_count=10)

        total = result1['success_count'] + result2['success_count']
        print(f"总共成功: {total}")

asyncio.run(main())
```

---

## 📁 重要文件

| 文件 | 用途 |
|------|------|
| `test_auto_greeting.py` | 完整测试脚本（推荐用于测试） |
| `auto_greeting_reusable.py` | 可重用函数库（推荐用于集成） |
| `AUTO_GREETING_GUIDE.md` | 详细使用指南 |
| `AUTO_GREETING_TECHNICAL.md` | 技术细节文档 |

---

## ⚙️ 配置选项

```python
# 基本配置
result = await auto_greet_candidates(
    target_count=10,       # 打招呼数量
    auth_file='boss_auth.json',  # 登录文件
    headless=False         # 是否无头模式
)
```

---

## 🎯 成功率

- **测试成功率**: 100% (10/10)
- **平均速度**: 9.5秒/人
- **建议批次**: 20-50人/批

---

## ⚠️ 注意事项

1. ✅ 确保登录状态有效
2. ✅ 不要设置过快的速度
3. ✅ 建议分批处理大量候选人
4. ✅ 注意每日沟通次数限制

---

## 💡 常见问题

### Q: 如何查看详细日志？
A: 日志会自动输出到控制台，包含每一步的详细信息

### Q: 如果某个候选人失败了怎么办？
A: 脚本会自动继续处理下一个，不会中断

### Q: 能否自定义招呼消息？
A: 当前版本使用默认消息，后续版本会支持

### Q: 如何提高速度？
A: 不建议提高速度，容易被识别为机器人

---

## 📞 获取帮助

- 查看 [详细指南](./AUTO_GREETING_GUIDE.md)
- 查看 [技术文档](./AUTO_GREETING_TECHNICAL.md)
- 查看 [项目总结](./AUTO_GREETING_SUMMARY.md)

---

**版本**: v1.0
**状态**: ✅ 可用
**测试**: ✅ 通过
