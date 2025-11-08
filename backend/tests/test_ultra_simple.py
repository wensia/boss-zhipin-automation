"""
超简单测试 - 打印所有包含"K"的元素
"""
import asyncio
import logging
from pathlib import Path
from app.services.boss_automation import BossAutomation

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)


async def ultra_simple():
    """超简单测试"""
    automation = BossAutomation()

    try:
        logger.info("=" * 80)
        logger.info("🔍 超简单测试")
        logger.info("=" * 80)

        # 初始化
        await automation.initialize(headless=False)
        await asyncio.sleep(2)

        # 登录检查
        login_status = await automation.check_login_status()
        if not login_status.get('logged_in'):
            logger.error("❌ 未登录")
            return

        # 导航到推荐页面
        logger.info("\n📍 导航到推荐页面...")
        await automation.navigate_to_recommend_page()

        # 等待页面加载
        logger.info("⏳ 等待15秒...")
        await asyncio.sleep(15)

        # 截图
        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "ultra_01.png"))

        # 方法1: 使用 Playwright 的文本选择器
        logger.info("\n" + "=" * 80)
        logger.info("方法1: 使用 Playwright text 选择器查找包含'新媒体'的元素")
        logger.info("=" * 80)

        try:
            elements = await automation.page.query_selector_all("text=/新媒体/")
            logger.info(f"找到 {len(elements)} 个包含'新媒体'的元素")

            for idx, elem in enumerate(elements[:10], 1):
                text = await elem.text_content()
                html = await elem.evaluate("el => el.outerHTML")
                logger.info(f"\n元素 {idx}:")
                logger.info(f"  文本: {text[:150]}")
                logger.info(f"  HTML: {html[:200]}")
        except Exception as e:
            logger.error(f"查找失败: {e}")

        # 方法2: 查找所有包含特定薪资格式的元素
        logger.info("\n" + "=" * 80)
        logger.info("方法2: 使用正则表达式查找薪资格式")
        logger.info("=" * 80)

        try:
            # 查找包含 "5-10K" 格式的元素
            elements = await automation.page.query_selector_all("text=/\\d+-\\d+K/")
            logger.info(f"找到 {len(elements)} 个包含薪资格式的元素")

            for idx, elem in enumerate(elements[:10], 1):
                text = await elem.text_content()
                bounding_box = await elem.bounding_box()
                logger.info(f"\n元素 {idx}:")
                logger.info(f"  文本: {text[:150]}")
                if bounding_box:
                    logger.info(f"  位置: x={bounding_box['x']:.0f}, y={bounding_box['y']:.0f}, width={bounding_box['width']:.0f}")
        except Exception as e:
            logger.error(f"查找失败: {e}")

        # 方法3: 直接查找包含"天津"的元素
        logger.info("\n" + "=" * 80)
        logger.info("方法3: 查找包含'天津'的元素")
        logger.info("=" * 80)

        try:
            elements = await automation.page.query_selector_all("text=/天津/")
            logger.info(f"找到 {len(elements)} 个包含'天津'的元素")

            # 过滤出位置在顶部的元素
            top_elements = []
            for elem in elements:
                bounding_box = await elem.bounding_box()
                if bounding_box and bounding_box['y'] < 200:
                    top_elements.append((elem, bounding_box))

            logger.info(f"其中 {len(top_elements)} 个在页面顶部(y<200)")

            for idx, (elem, bbox) in enumerate(top_elements[:5], 1):
                text = await elem.text_content()
                html = await elem.evaluate("el => el.outerHTML")
                logger.info(f"\n元素 {idx}:")
                logger.info(f"  位置: x={bbox['x']:.0f}, y={bbox['y']:.0f}, width={bbox['width']:.0f}")
                logger.info(f"  文本: {text[:150]}")
                logger.info(f"  HTML: {html[:300]}")
        except Exception as e:
            logger.error(f"查找失败: {e}")

        # 方法4: 使用 XPath
        logger.info("\n" + "=" * 80)
        logger.info("方法4: 使用 XPath 查找包含职位信息的元素")
        logger.info("=" * 80)

        try:
            # 查找包含 "K" 且文本长度适中的元素
            elements = await automation.page.query_selector_all("//*[contains(text(), 'K') and contains(text(), '_')]")
            logger.info(f"找到 {len(elements)} 个包含'K'和'_'的元素")

            for idx, elem in enumerate(elements[:10], 1):
                text = await elem.text_content()
                tag_name = await elem.evaluate("el => el.tagName")
                class_name = await elem.evaluate("el => el.className")
                bounding_box = await elem.bounding_box()

                logger.info(f"\n元素 {idx}:")
                logger.info(f"  标签: {tag_name}")
                logger.info(f"  类名: {class_name}")
                if bounding_box:
                    logger.info(f"  位置: x={bounding_box['x']:.0f}, y={bounding_box['y']:.0f}")
                logger.info(f"  文本: {text[:150]}")
        except Exception as e:
            logger.error(f"查找失败: {e}")

        logger.info("\n⏳ 浏览器将保持打开 120 秒...")
        await asyncio.sleep(120)

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}", exc_info=True)

    finally:
        await automation.cleanup()


if __name__ == "__main__":
    asyncio.run(ultra_simple())
