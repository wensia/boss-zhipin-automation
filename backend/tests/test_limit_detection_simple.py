"""
简单测试：验证优化后的限制弹窗检测功能
"""
import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.boss_automation import BossAutomation
from app.services.greeting_service import greeting_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_limit_detection():
    """测试优化后的限制弹窗检测"""

    automation = BossAutomation()

    try:
        # 初始化浏览器
        await automation.initialize(headless=False)
        logger.info("✅ 浏览器初始化成功")

        # 检查登录状态
        login_result = await automation.check_login_status()
        if not login_result.get('logged_in'):
            logger.error("❌ 未登录，请先登录")
            return

        logger.info(f"✅ 已登录: {login_result.get('user_info', {}).get('showName')}")

        # 导航到推荐页面
        await automation.navigate_to_recommend_page()
        logger.info("✅ 已导航到推荐页面")

        # 等待页面加载
        await asyncio.sleep(3)

        # 获取 iframe
        recommend_frame = None
        for frame in automation.page.frames:
            if frame.name == 'recommendFrame':
                recommend_frame = frame
                break

        if not recommend_frame:
            logger.error("❌ 未找到 recommendFrame")
            return

        logger.info("✅ 找到推荐页面 iframe")

        # 设置 greeting_manager 的 automation 引用
        greeting_manager.automation = automation

        # 尝试点击第一个候选人的打招呼按钮
        logger.info("🖱️ 尝试触发打招呼...")

        try:
            # 点击第一个候选人
            first_card = recommend_frame.locator('ul.card-list > li:nth-child(1)').first
            await first_card.wait_for(state='visible', timeout=5000)

            name_el = first_card.locator('.name').first
            candidate_name = await name_el.inner_text() if await name_el.count() > 0 else "候选人1"
            logger.info(f"📋 候选人: {candidate_name}")

            await first_card.click()
            await asyncio.sleep(2)

            # 等待简历面板
            await recommend_frame.wait_for_selector('.dialog-lib-resume', timeout=10000)
            logger.info("✅ 简历面板已加载")

            # 查找打招呼按钮
            button_selectors = [
                '.dialog-lib-resume .button-list-wrap button',
                '.dialog-lib-resume .communication button',
                '.resume-right-side .communication button',
            ]

            button = None
            for selector in button_selectors:
                try:
                    btn = recommend_frame.locator(selector).first
                    if await btn.count() > 0 and await btn.is_visible():
                        text = await btn.inner_text()
                        logger.info(f"找到按钮: '{text}'")
                        button = btn
                        break
                except:
                    continue

            if button:
                # 点击打招呼按钮
                await button.click()
                logger.info("✅ 已点击打招呼按钮")

                # 等待2秒，让限制弹窗出现
                await asyncio.sleep(2)

                # 测试检测功能
                logger.info("="*80)
                logger.info("🔍 测试优化后的限制弹窗检测...")
                logger.info("="*80)

                detected = await greeting_manager._check_limit_dialog()

                if detected:
                    logger.info("="*80)
                    logger.info("✅ 检测成功！限制弹窗已被正确识别")
                    logger.info("="*80)
                else:
                    logger.warning("="*80)
                    logger.warning("⚠️ 未检测到限制弹窗")
                    logger.warning("如果弹窗确实出现了，可能需要进一步优化检测逻辑")
                    logger.warning("="*80)
            else:
                logger.warning("⚠️ 未找到打招呼按钮")

        except Exception as e:
            logger.error(f"❌ 触发打招呼失败: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}", exc_info=True)

    finally:
        # 清理
        try:
            await automation.cleanup()
            logger.info("✅ 清理完成")
        except:
            pass


async def main():
    """主函数"""
    logger.info("="*80)
    logger.info("🚀 开始测试优化后的限制弹窗检测功能")
    logger.info("="*80)
    logger.info("")
    logger.info("说明：")
    logger.info("  1. 确保已经达到打招呼上限")
    logger.info("  2. 脚本会尝试触发打招呼")
    logger.info("  3. 使用优化后的检测逻辑判断是否出现限制弹窗")
    logger.info("")
    logger.info("="*80)

    await test_limit_detection()


if __name__ == "__main__":
    asyncio.run(main())
