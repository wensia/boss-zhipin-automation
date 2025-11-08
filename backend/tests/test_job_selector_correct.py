"""
使用正确的选择器测试职位列表获取
等待 #headerWrap 出现后再操作
"""
import asyncio
import logging
from pathlib import Path
from app.services.boss_automation import BossAutomation

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)


async def test_correct_selector():
    """使用正确的选择器测试"""
    automation = BossAutomation()

    try:
        logger.info("=" * 80)
        logger.info("🧪 使用正确选择器测试职位获取")
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
        await asyncio.sleep(3)

        logger.info(f"✅ 当前URL: {automation.page.url}")

        # 等待 #headerWrap 出现
        logger.info("\n📍 等待 #headerWrap 元素出现...")
        try:
            await automation.page.wait_for_selector('#headerWrap', timeout=10000)
            logger.info("✅ #headerWrap 已出现")
        except Exception as e:
            logger.error(f"❌ #headerWrap 未出现: {e}")

            # 尝试刷新页面
            logger.info("🔄 尝试刷新页面...")
            await automation.page.reload(wait_until='networkidle')
            await asyncio.sleep(3)

            try:
                await automation.page.wait_for_selector('#headerWrap', timeout=10000)
                logger.info("✅ 刷新后 #headerWrap 已出现")
            except:
                logger.error("❌ 刷新后 #headerWrap 仍未出现")
                # 截图调试
                await automation.page.screenshot(path=str(SCREENSHOT_DIR / "no_headerWrap.png"))
                logger.info("📸 已保存截图: no_headerWrap.png")
                return

        # 截图
        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "with_headerWrap.png"))
        logger.info("📸 已保存截图: with_headerWrap.png")

        # 使用正确的选择器
        logger.info("\n" + "=" * 80)
        logger.info("📍 使用正确的选择器点击职位选择器")
        logger.info("=" * 80)

        trigger_selector = "#headerWrap > div > div > div.ui-dropmenu.ui-dropmenu-label-arrow.ui-dropmenu-drop-arrow.job-selecter-wrap > div.ui-dropmenu-label"

        # 等待触发器出现
        logger.info(f"⏳ 等待触发器: {trigger_selector}")
        try:
            trigger_element = await automation.page.wait_for_selector(trigger_selector, timeout=10000)
            logger.info("✅ 触发器已找到")
        except Exception as e:
            logger.error(f"❌ 触发器未找到: {e}")
            return

        # 获取触发器显示的文本
        trigger_text = await trigger_element.text_content()
        logger.info(f"📝 触发器文本: {trigger_text.strip()}")

        # 截图（点击前）
        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "before_click_correct.png"))

        # 点击触发器
        logger.info("👆 点击触发器...")
        await trigger_element.click()
        await asyncio.sleep(2)

        # 截图（点击后）
        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "after_click_correct.png"))
        logger.info("📸 已保存点击后截图")

        # 查找下拉列表
        logger.info("\n" + "=" * 80)
        logger.info("📍 查找下拉列表")
        logger.info("=" * 80)

        list_selector = "#headerWrap > div > div > div.ui-dropmenu.ui-dropmenu-visible.ui-dropmenu-label-arrow.ui-dropmenu-drop-arrow.job-selecter-wrap.expanding > div.ui-dropmenu-list > ul"

        logger.info(f"⏳ 等待列表: {list_selector}")
        try:
            list_element = await automation.page.wait_for_selector(list_selector, timeout=5000)
            logger.info("✅ 列表已找到")
        except Exception as e:
            logger.warning(f"⚠️ 精确选择器未找到: {e}")
            logger.info("尝试使用备用选择器...")

            # 备用选择器
            backup_selectors = [
                ".job-selecter-wrap.expanding .ui-dropmenu-list ul",
                ".ui-dropmenu.expanding .ui-dropmenu-list ul",
                "#headerWrap .ui-dropmenu-list ul"
            ]

            list_element = None
            for selector in backup_selectors:
                try:
                    list_element = await automation.page.wait_for_selector(selector, timeout=3000)
                    logger.info(f"✅ 使用备用选择器找到列表: {selector}")
                    break
                except:
                    continue

            if not list_element:
                logger.error("❌ 所有选择器都未找到列表")
                return

        # 获取所有 li 元素
        logger.info("\n" + "=" * 80)
        logger.info("📍 获取职位列表")
        logger.info("=" * 80)

        # 先尝试 li.job-item
        job_items = await list_element.query_selector_all("li.job-item")
        logger.info(f"📋 找到 {len(job_items)} 个 li.job-item 元素")

        if len(job_items) == 0:
            # 尝试所有 li
            job_items = await list_element.query_selector_all("li")
            logger.info(f"📋 找到 {len(job_items)} 个 li 元素")

        # 遍历并提取信息
        jobs = []
        for idx, item in enumerate(job_items):
            try:
                # 获取 value 属性
                value = await item.get_attribute("value")

                # 获取文本
                label_element = await item.query_selector(".label")
                if label_element:
                    label_text = await label_element.text_content()
                else:
                    label_text = await item.text_content()

                label_text = label_text.strip() if label_text else ""

                # 获取 HTML（用于调试）
                html = await item.evaluate("el => el.outerHTML")

                logger.info(f"\n--- 职位 {idx + 1} ---")
                logger.info(f"value: {value}")
                logger.info(f"label: {label_text[:100]}")
                logger.info(f"HTML: {html[:150]}...")

                if value:
                    jobs.append({
                        'value': value,
                        'label': label_text
                    })
            except Exception as e:
                logger.warning(f"⚠️ 处理职位 {idx + 1} 失败: {e}")

        logger.info("\n" + "=" * 80)
        logger.info(f"✅ 成功提取 {len(jobs)} 个职位")
        logger.info("=" * 80)

        for idx, job in enumerate(jobs, 1):
            logger.info(f"\n职位 {idx}:")
            logger.info(f"  value: {job['value']}")
            logger.info(f"  label: {job['label']}")

        # 截图最终状态
        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "final_dropdown.png"))
        logger.info("\n📸 所有截图已保存到: screenshots/")

        # 保持浏览器打开
        logger.info("\n⏳ 浏览器将保持打开 60 秒...")
        await asyncio.sleep(60)

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}", exc_info=True)
        try:
            await automation.page.screenshot(path=str(SCREENSHOT_DIR / "error.png"))
        except:
            pass

    finally:
        await automation.cleanup()


if __name__ == "__main__":
    asyncio.run(test_correct_selector())
