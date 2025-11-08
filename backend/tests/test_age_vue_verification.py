#!/usr/bin/env python3
"""
年龄滑块Vue方法验证测试
使用MCP深度测试Vue组件方法的可靠性和准确性
"""

import asyncio
import logging
from pathlib import Path
from app.services.boss_automation import BossAutomation
from app.utils.age_filter import set_age_filter_via_vue, read_current_age_filter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCREENSHOT_DIR = Path(__file__).parent / "screenshots" / "vue_verification"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


class AgeFilterTester:
    """年龄筛选测试器"""

    def __init__(self, automation, frame, page):
        self.automation = automation
        self.frame = frame
        self.page = page
        self.test_results = []

    async def reset_filter_panel(self):
        """重置筛选面板"""
        try:
            # 点击取消
            cancel_btn = await self.frame.query_selector("text=取消")
            if cancel_btn:
                await cancel_btn.click()
                await asyncio.sleep(1)

            # 重新打开
            filter_btn = await self.frame.wait_for_selector(".recommend-filter", timeout=5000)
            await filter_btn.click()
            await asyncio.sleep(2)
            return True
        except Exception as e:
            logger.warning(f"重置筛选面板失败: {e}")
            return False

    async def test_single_age_range(self, test_num: int, min_age: int, max_age: int = None, description: str = ""):
        """
        测试单个年龄范围设置

        Args:
            test_num: 测试编号
            min_age: 最小年龄
            max_age: 最大年龄（None表示不限）
            description: 测试描述
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"测试 {test_num}: {description}")
        logger.info(f"目标年龄: {min_age} - {max_age if max_age else '不限'}")
        logger.info(f"{'='*70}")

        try:
            # 读取初始值
            initial = await read_current_age_filter(self.frame)
            logger.info(f"📌 初始年龄: {initial['min']} - {initial['max']}")

            # 设置年龄
            logger.info(f"🎯 开始设置年龄...")
            result = await set_age_filter_via_vue(self.frame, min_age, max_age)

            # 输出日志
            if result.get('logs'):
                for log in result['logs']:
                    logger.info(f"   - {log}")

            # 验证结果
            if result['success']:
                final = result.get('final_values')
                if final:
                    logger.info(f"✅ 最终年龄: {final['min']} - {final['max']}")

                    # 检查是否匹配
                    expected_max = str(max_age) if max_age else "不限"
                    min_match = final['min'] == str(min_age)
                    max_match = final['max'] == expected_max

                    if min_match and max_match:
                        logger.info(f"🎉 完全匹配！设置成功")
                        status = "success"
                    else:
                        logger.warning(f"⚠️  部分匹配: 最小年龄{'✅' if min_match else '❌'}, 最大年龄{'✅' if max_match else '❌'}")
                        status = "partial"
                else:
                    logger.warning("⚠️  无法读取最终值")
                    status = "unknown"
            else:
                logger.error(f"❌ 设置失败: {result.get('error', '未知错误')}")
                status = "failed"

            # 截图
            screenshot_name = f"test{test_num:02d}_{min_age}_{max_age if max_age else 'unlimited'}.png"
            await self.page.screenshot(
                path=str(SCREENSHOT_DIR / screenshot_name),
                full_page=True
            )
            logger.info(f"📸 截图: {screenshot_name}")

            # 记录结果
            self.test_results.append({
                'test_num': test_num,
                'description': description,
                'target': {'min': min_age, 'max': max_age},
                'result': result,
                'status': status,
                'screenshot': screenshot_name
            })

            return status == "success"

        except Exception as e:
            logger.exception(f"❌ 测试{test_num}出错: {e}")
            self.test_results.append({
                'test_num': test_num,
                'description': description,
                'target': {'min': min_age, 'max': max_age},
                'error': str(e),
                'status': 'error'
            })
            return False

    async def run_all_tests(self):
        """运行所有测试用例"""
        logger.info("="*80)
        logger.info("🚀 开始Vue组件方法验证测试")
        logger.info("="*80)

        # 测试用例列表
        test_cases = [
            # (min_age, max_age, description)
            (20, 25, "年轻群体 20-25岁"),
            (25, 35, "主力群体 25-35岁"),
            (30, 45, "资深人才 30-45岁"),
            (22, 28, "精确范围 22-28岁"),
            (35, None, "35岁以上不限"),
            (18, None, "18岁以上不限"),
            (28, 32, "窄范围 28-32岁"),
            (16, 24, "最小起点 16-24岁"),
            (40, 50, "高年龄段 40-50岁"),
            (25, 40, "常用范围 25-40岁"),
        ]

        success_count = 0
        total_count = len(test_cases)

        for i, (min_age, max_age, description) in enumerate(test_cases, 1):
            # 每个测试前重置面板
            if i > 1:
                logger.info("\n⏸️  等待3秒后继续下一个测试...")
                await asyncio.sleep(3)
                await self.reset_filter_panel()

            # 执行测试
            success = await self.test_single_age_range(i, min_age, max_age, description)
            if success:
                success_count += 1

        return success_count, total_count

    def print_summary(self, success_count: int, total_count: int):
        """打印测试摘要"""
        logger.info("\n" + "="*80)
        logger.info("📊 测试结果汇总")
        logger.info("="*80)

        logger.info(f"\n总测试数: {total_count}")
        logger.info(f"成功: {success_count}")
        logger.info(f"失败: {total_count - success_count}")
        logger.info(f"成功率: {success_count/total_count*100:.1f}%")

        logger.info("\n详细结果:")
        logger.info("-" * 80)

        for result in self.test_results:
            status_emoji = {
                'success': '✅',
                'partial': '⚠️',
                'failed': '❌',
                'error': '💥',
                'unknown': '❓'
            }.get(result.get('status'), '❓')

            target = result['target']
            max_str = target['max'] if target['max'] else '不限'

            logger.info(f"{status_emoji} 测试{result['test_num']:2d}: {result['description']}")
            logger.info(f"           目标: {target['min']}-{max_str}")

            if result.get('result'):
                final = result['result'].get('final_values')
                if final:
                    logger.info(f"           实际: {final['min']}-{final['max']}")

        logger.info("="*80)

        # 生成测试报告文件
        report_path = Path(__file__).parent / "age_vue_verification_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("年龄滑块Vue方法验证测试报告\n")
            f.write("="*80 + "\n\n")

            f.write(f"测试时间: {asyncio.get_event_loop().time()}\n")
            f.write(f"总测试数: {total_count}\n")
            f.write(f"成功: {success_count}\n")
            f.write(f"失败: {total_count - success_count}\n")
            f.write(f"成功率: {success_count/total_count*100:.1f}%\n\n")

            f.write("详细结果:\n")
            f.write("-" * 80 + "\n")

            for result in self.test_results:
                status_emoji = {
                    'success': '✅',
                    'partial': '⚠️',
                    'failed': '❌',
                    'error': '💥',
                    'unknown': '❓'
                }.get(result.get('status'), '❓')

                target = result['target']
                max_str = target['max'] if target['max'] else '不限'

                f.write(f"\n{status_emoji} 测试{result['test_num']:2d}: {result['description']}\n")
                f.write(f"   目标: {target['min']}-{max_str}\n")

                if result.get('result'):
                    final = result['result'].get('final_values')
                    if final:
                        f.write(f"   实际: {final['min']}-{final['max']}\n")

                if result.get('screenshot'):
                    f.write(f"   截图: {result['screenshot']}\n")

        logger.info(f"\n📄 测试报告已保存: {report_path}")


async def main():
    """主函数"""
    automation = BossAutomation()

    try:
        logger.info("="*80)
        logger.info("🔬 年龄滑块Vue方法深度验证测试")
        logger.info("="*80)

        # 初始化
        logger.info("\n🚀 初始化浏览器...")
        await automation.initialize(headless=False)
        await asyncio.sleep(2)

        # 登录检查
        logger.info("🔐 检查登录状态...")
        login_status = await automation.check_login_status()
        if not login_status.get('logged_in'):
            logger.error("❌ 未登录，请先登录Boss直聘")
            return

        logger.info("✅ 已登录")

        # 导航到推荐页面
        logger.info("🧭 导航到推荐页面...")
        await automation.navigate_to_recommend_page()
        await asyncio.sleep(3)

        # 获取iframe
        logger.info("🔍 查找recommendFrame...")
        recommend_frame = None
        for frame in automation.page.frames:
            if frame.name == 'recommendFrame':
                recommend_frame = frame
                break

        if not recommend_frame:
            logger.error("❌ 未找到 recommendFrame iframe")
            return

        logger.info("✅ 找到 recommendFrame")

        # 打开筛选弹窗
        logger.info("📂 打开筛选面板...")
        filter_btn = await recommend_frame.wait_for_selector(".recommend-filter", timeout=10000)
        await filter_btn.click()
        await asyncio.sleep(2)

        await automation.page.screenshot(
            path=str(SCREENSHOT_DIR / "initial_state.png"),
            full_page=True
        )
        logger.info("✅ 筛选面板已打开")

        # 创建测试器
        tester = AgeFilterTester(automation, recommend_frame, automation.page)

        # 运行所有测试
        success_count, total_count = await tester.run_all_tests()

        # 打印摘要
        tester.print_summary(success_count, total_count)

        # 最终评估
        success_rate = success_count / total_count * 100
        logger.info("\n" + "="*80)
        if success_rate == 100:
            logger.info("🎉🎉🎉 完美！所有测试都通过了！")
        elif success_rate >= 80:
            logger.info(f"✅ 很好！{success_rate:.1f}% 的测试通过")
        elif success_rate >= 50:
            logger.info(f"⚠️  一般。{success_rate:.1f}% 的测试通过")
        else:
            logger.info(f"❌ 需要改进。只有 {success_rate:.1f}% 的测试通过")
        logger.info("="*80)

        # 保持页面打开
        logger.info("\n按 Ctrl+C 退出...")
        await asyncio.sleep(300)

    except KeyboardInterrupt:
        logger.info("\n👋 用户中断")
    except Exception as e:
        logger.exception(f"❌ 测试出错: {e}")
    finally:
        logger.info("🛑 关闭浏览器...")
        await automation.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
