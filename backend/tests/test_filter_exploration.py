"""
全面探索推荐页面的筛选功能
测试流程：
1. 找到并点击筛选按钮
2. 分析筛选弹窗中所有组件的选择器和交互方式
3. 测试选中多个条件
4. 点击确定按钮
5. 总结实现方案
"""
import asyncio
import logging
from pathlib import Path
from app.services.boss_automation import BossAutomation

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)


async def test_filter_exploration():
    """全面探索筛选功能"""
    automation = BossAutomation()

    try:
        logger.info("=" * 80)
        logger.info("🧪 开始探索推荐页面筛选功能")
        logger.info("=" * 80)

        # 初始化
        await automation.initialize(headless=False)
        await asyncio.sleep(2)

        # 登录检查
        login_status = await automation.check_login_status()
        if not login_status.get('logged_in'):
            logger.error("❌ 未登录")
            return

        logger.info("✅ 已登录")

        # 导航到推荐页面
        logger.info("\n📍 导航到推荐页面...")
        await automation.navigate_to_recommend_page()
        await asyncio.sleep(3)

        # 查找 recommendFrame iframe
        logger.info("\n" + "=" * 80)
        logger.info("🔍 步骤1: 查找 recommendFrame iframe")
        logger.info("=" * 80)

        recommend_frame = None
        for frame in automation.page.frames:
            if frame.name == 'recommendFrame':
                recommend_frame = frame
                logger.info(f"✅ 找到 recommendFrame: {frame.url}")
                break

        if not recommend_frame:
            logger.error("❌ 未找到 recommendFrame iframe")
            return

        # 截图当前页面
        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "01_before_filter.png"))
        logger.info("📸 已保存初始截图")

        # 步骤2: 查找并点击筛选按钮
        logger.info("\n" + "=" * 80)
        logger.info("🔍 步骤2: 查找并点击筛选按钮")
        logger.info("=" * 80)

        # 用户提供的选择器
        filter_button_selector = "#headerWrap > div > div > div.fl.recommend-filter.op-filter > div > div"

        logger.info(f"尝试选择器: {filter_button_selector}")

        # 先尝试简化的选择器
        simplified_selectors = [
            ".recommend-filter",
            ".op-filter",
            "[class*='recommend-filter']",
            "[class*='op-filter']",
        ]

        filter_button = None
        for selector in [filter_button_selector] + simplified_selectors:
            try:
                logger.info(f"  尝试: {selector}")
                element = await recommend_frame.query_selector(selector)
                if element:
                    # 检查元素是否可见
                    is_visible = await element.is_visible()
                    logger.info(f"  ✅ 找到元素，可见: {is_visible}")
                    if is_visible:
                        filter_button = element
                        logger.info(f"  ✅ 使用选择器: {selector}")
                        break
            except Exception as e:
                logger.info(f"  ❌ 失败: {e}")

        if not filter_button:
            # 尝试查找包含"筛选"文字的元素
            logger.info("  尝试通过文本查找...")
            try:
                filter_button = await recommend_frame.query_selector("text=筛选")
                if filter_button:
                    logger.info("  ✅ 通过文本找到筛选按钮")
            except:
                pass

        if not filter_button:
            logger.error("❌ 未找到筛选按钮")
            # 保存页面HTML用于调试
            content = await recommend_frame.content()
            debug_file = SCREENSHOT_DIR / "frame_html_debug.html"
            debug_file.write_text(content, encoding='utf-8')
            logger.info(f"已保存iframe HTML到: {debug_file}")
            return

        # 点击筛选按钮
        logger.info("🖱️  点击筛选按钮...")
        await filter_button.click()
        await asyncio.sleep(2)

        # 截图弹出的筛选框
        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "02_filter_dialog_opened.png"))
        logger.info("📸 已保存筛选框截图")

        # 步骤3: 分析筛选弹窗中的所有组件
        logger.info("\n" + "=" * 80)
        logger.info("🔍 步骤3: 分析筛选弹窗组件")
        logger.info("=" * 80)

        # 查找筛选弹窗容器
        dialog_selectors = [
            ".dialog-wrap",
            "[class*='dialog']",
            "[class*='filter-dialog']",
            ".filter-container",
        ]

        dialog = None
        for selector in dialog_selectors:
            try:
                element = await recommend_frame.query_selector(selector)
                if element and await element.is_visible():
                    dialog = element
                    logger.info(f"✅ 找到筛选弹窗容器: {selector}")
                    break
            except:
                pass

        if dialog:
            # 分析弹窗中的各类组件
            logger.info("\n📊 分析筛选条件组件:")

            # 1. 年龄滑动条
            logger.info("\n  1️⃣ 年龄范围:")
            age_selectors = [
                "input[type='number']",
                "[class*='age']",
                "[class*='slider']",
            ]
            for selector in age_selectors:
                elements = await dialog.query_selector_all(selector)
                if elements:
                    logger.info(f"    找到 {len(elements)} 个元素: {selector}")

            # 2. 按钮组（专业、活跃度等）
            logger.info("\n  2️⃣ 按钮组:")
            button_selectors = [
                "button",
                "[role='button']",
                ".btn",
                "[class*='button']",
                "[class*='item']",
            ]
            for selector in button_selectors:
                elements = await dialog.query_selector_all(selector)
                if elements:
                    logger.info(f"    找到 {len(elements)} 个元素: {selector}")
                    # 获取前3个按钮的文本
                    for i, el in enumerate(elements[:3]):
                        try:
                            text = await el.text_content()
                            if text and text.strip():
                                logger.info(f"      [{i}] 文本: {text.strip()}")
                        except:
                            pass

            # 3. 单选/多选框
            logger.info("\n  3️⃣ 单选/多选框:")
            checkbox_selectors = [
                "input[type='checkbox']",
                "input[type='radio']",
                "[class*='checkbox']",
                "[class*='radio']",
            ]
            for selector in checkbox_selectors:
                elements = await dialog.query_selector_all(selector)
                if elements:
                    logger.info(f"    找到 {len(elements)} 个元素: {selector}")

            # 4. 确定和取消按钮
            logger.info("\n  4️⃣ 确定和取消按钮:")
            confirm_button = await dialog.query_selector("text=确定")
            cancel_button = await dialog.query_selector("text=取消")

            if confirm_button:
                logger.info("    ✅ 找到确定按钮")
            if cancel_button:
                logger.info("    ✅ 找到取消按钮")

        # 步骤4: 测试选中多个条件
        logger.info("\n" + "=" * 80)
        logger.info("🔍 步骤4: 测试选中筛选条件")
        logger.info("=" * 80)

        # 尝试选中"今日活跃"
        logger.info("\n  测试1: 选中'今日活跃'")
        try:
            active_today = await recommend_frame.query_selector("text=今日活跃")
            if active_today:
                await active_today.click()
                await asyncio.sleep(1)
                logger.info("    ✅ 已点击'今日活跃'")
                await automation.page.screenshot(path=str(SCREENSHOT_DIR / "03_selected_active_today.png"))
        except Exception as e:
            logger.error(f"    ❌ 失败: {e}")

        # 尝试选中"男"
        logger.info("\n  测试2: 选中'男'")
        try:
            gender_male = await recommend_frame.query_selector("text=男")
            if gender_male:
                await gender_male.click()
                await asyncio.sleep(1)
                logger.info("    ✅ 已点击'男'")
                await automation.page.screenshot(path=str(SCREENSHOT_DIR / "04_selected_gender.png"))
        except Exception as e:
            logger.error(f"    ❌ 失败: {e}")

        # 尝试选中"本科"
        logger.info("\n  测试3: 选中'本科'")
        try:
            education = await recommend_frame.query_selector("text=本科")
            if education:
                await education.click()
                await asyncio.sleep(1)
                logger.info("    ✅ 已点击'本科'")
                await automation.page.screenshot(path=str(SCREENSHOT_DIR / "05_selected_education.png"))
        except Exception as e:
            logger.error(f"    ❌ 失败: {e}")

        # 步骤5: 点击确定按钮
        logger.info("\n" + "=" * 80)
        logger.info("🔍 步骤5: 点击确定按钮")
        logger.info("=" * 80)

        try:
            confirm_button = await recommend_frame.query_selector("text=确定")
            if confirm_button:
                await confirm_button.click()
                await asyncio.sleep(2)
                logger.info("✅ 已点击确定按钮")
                await automation.page.screenshot(path=str(SCREENSHOT_DIR / "06_after_confirm.png"))
            else:
                logger.error("❌ 未找到确定按钮")
        except Exception as e:
            logger.error(f"❌ 点击确定失败: {e}")

        # 总结
        logger.info("\n" + "=" * 80)
        logger.info("📋 测试总结")
        logger.info("=" * 80)
        logger.info("✅ 已完成筛选功能探索")
        logger.info("📸 所有截图已保存到 screenshots/ 目录")
        logger.info(f"   - 01_before_filter.png: 初始页面")
        logger.info(f"   - 02_filter_dialog_opened.png: 筛选框打开")
        logger.info(f"   - 03_selected_active_today.png: 选中'今日活跃'")
        logger.info(f"   - 04_selected_gender.png: 选中'男'")
        logger.info(f"   - 05_selected_education.png: 选中'本科'")
        logger.info(f"   - 06_after_confirm.png: 点击确定后")

        # 保持浏览器打开60秒
        logger.info("\n⏳ 浏览器将保持打开 60 秒供观察...")
        await asyncio.sleep(60)

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}", exc_info=True)

    finally:
        await automation.cleanup()


if __name__ == "__main__":
    asyncio.run(test_filter_exploration())
