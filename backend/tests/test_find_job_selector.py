"""
精确查找职位选择器
在推荐页面查找包含"职位"相关文本的所有元素
"""
import asyncio
import logging
from pathlib import Path
from app.services.boss_automation import BossAutomation

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)


async def find_job_selector():
    """精确查找职位选择器"""
    automation = BossAutomation()

    try:
        logger.info("=" * 80)
        logger.info("🔍 精确查找职位选择器")
        logger.info("=" * 80)

        # 初始化
        await automation.initialize(headless=False)
        await asyncio.sleep(2)

        # 检查登录
        login_status = await automation.check_login_status()
        if not login_status.get('logged_in'):
            logger.error("❌ 未登录")
            return

        # 导航到推荐页面
        await automation.navigate_to_recommend_page()
        await asyncio.sleep(3)

        logger.info(f"✅ 当前URL: {automation.page.url}")

        # 截图整个页面
        screenshot_path = SCREENSHOT_DIR / "recommend_page_full.png"
        await automation.page.screenshot(path=str(screenshot_path), full_page=True)
        logger.info(f"📸 完整页面截图: {screenshot_path}")

        # 方法 1: 查找包含"职位"文本的所有元素
        logger.info("\n" + "=" * 80)
        logger.info("方法 1: 查找包含'职位'文本的元素")
        logger.info("=" * 80)

        job_related_elements = await automation.page.evaluate("""
            () => {
                const elements = [];
                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_TEXT,
                    null,
                    false
                );

                const jobKeywords = ['职位', '岗位', '招聘', 'job', 'position'];
                const foundElements = new Set();

                let node;
                while (node = walker.nextNode()) {
                    const text = node.textContent.trim();
                    if (text && jobKeywords.some(keyword => text.includes(keyword))) {
                        let element = node.parentElement;
                        // 向上找到可点击的元素
                        while (element && element !== document.body) {
                            if (!foundElements.has(element)) {
                                foundElements.add(element);

                                const rect = element.getBoundingClientRect();
                                const isVisible = rect.width > 0 && rect.height > 0 &&
                                                window.getComputedStyle(element).visibility !== 'hidden';

                                if (isVisible) {
                                    elements.push({
                                        tagName: element.tagName,
                                        className: element.className,
                                        id: element.id,
                                        text: text.substring(0, 100),
                                        selector: element.className ? `.${element.className.split(' ')[0]}` : element.tagName,
                                        hasClick: element.onclick !== null ||
                                                 element.getAttribute('onclick') !== null ||
                                                 window.getComputedStyle(element).cursor === 'pointer',
                                        position: {
                                            top: rect.top,
                                            left: rect.left,
                                            width: rect.width,
                                            height: rect.height
                                        }
                                    });
                                    break;
                                }
                            }
                            element = element.parentElement;
                        }
                    }
                }

                return elements;
            }
        """)

        logger.info(f"\n找到 {len(job_related_elements)} 个包含'职位'相关文本的元素:")
        for idx, elem in enumerate(job_related_elements[:10], 1):
            logger.info(f"\n元素 {idx}:")
            logger.info(f"  标签: {elem['tagName']}")
            logger.info(f"  类名: {elem['className']}")
            logger.info(f"  ID: {elem['id']}")
            logger.info(f"  文本: {elem['text']}")
            logger.info(f"  选择器: {elem['selector']}")
            logger.info(f"  可点击: {elem['hasClick']}")
            logger.info(f"  位置: top={elem['position']['top']}, left={elem['position']['left']}")

        # 方法 2: 查找所有下拉菜单元素
        logger.info("\n" + "=" * 80)
        logger.info("方法 2: 查找所有下拉菜单元素")
        logger.info("=" * 80)

        dropdown_elements = await automation.page.evaluate("""
            () => {
                const dropdowns = [];

                // 查找所有可能的下拉菜单类名
                const dropdownSelectors = [
                    '[class*="dropdown"]',
                    '[class*="select"]',
                    '[class*="picker"]',
                    '[class*="menu"]',
                    '[class*="dropmenu"]'
                ];

                dropdownSelectors.forEach(selector => {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach(elem => {
                        const rect = elem.getBoundingClientRect();
                        const isVisible = rect.width > 0 && rect.height > 0 &&
                                        rect.top >= 0 && rect.top < window.innerHeight;

                        if (isVisible) {
                            dropdowns.push({
                                tagName: elem.tagName,
                                className: elem.className,
                                id: elem.id,
                                text: elem.textContent.trim().substring(0, 100),
                                hasChild: elem.children.length > 0,
                                position: {
                                    top: rect.top,
                                    left: rect.left,
                                    width: rect.width,
                                    height: rect.height
                                }
                            });
                        }
                    });
                });

                return dropdowns;
            }
        """)

        logger.info(f"\n找到 {len(dropdown_elements)} 个下拉菜单元素:")
        for idx, elem in enumerate(dropdown_elements[:15], 1):
            logger.info(f"\n下拉菜单 {idx}:")
            logger.info(f"  类名: {elem['className']}")
            logger.info(f"  文本: {elem['text']}")
            logger.info(f"  位置: top={elem['position']['top']:.0f}, left={elem['position']['left']:.0f}")

        # 方法 3: 查找页面顶部区域（y < 150）的可点击元素
        logger.info("\n" + "=" * 80)
        logger.info("方法 3: 查找页面顶部区域的可点击元素")
        logger.info("=" * 80)

        top_clickable_elements = await automation.page.evaluate("""
            () => {
                const elements = [];
                const allElements = document.querySelectorAll('*');

                allElements.forEach(elem => {
                    const rect = elem.getBoundingClientRect();
                    const style = window.getComputedStyle(elem);

                    // 只查找顶部150px区域内的元素
                    if (rect.top >= 0 && rect.top < 150 &&
                        rect.width > 50 && rect.height > 20 &&
                        (style.cursor === 'pointer' || elem.onclick !== null)) {

                        elements.push({
                            tagName: elem.tagName,
                            className: elem.className,
                            id: elem.id,
                            text: elem.textContent.trim().substring(0, 100),
                            cursor: style.cursor,
                            position: {
                                top: rect.top,
                                left: rect.left,
                                width: rect.width,
                                height: rect.height
                            }
                        });
                    }
                });

                return elements;
            }
        """)

        logger.info(f"\n找到 {len(top_clickable_elements)} 个顶部可点击元素:")
        for idx, elem in enumerate(top_clickable_elements[:20], 1):
            logger.info(f"\n可点击元素 {idx}:")
            logger.info(f"  类名: {elem['className']}")
            logger.info(f"  文本: {elem['text']}")
            logger.info(f"  位置: top={elem['position']['top']:.0f}, left={elem['position']['left']:.0f}, width={elem['position']['width']:.0f}")

        # 等待用户手动检查
        logger.info("\n" + "=" * 80)
        logger.info("✅ 搜索完成！")
        logger.info("=" * 80)
        logger.info("📸 请查看截图: recommend_page_full.png")
        logger.info("📋 请在上面的输出中查找职位选择器")
        logger.info("\n⏳ 浏览器将保持打开 120 秒...")
        logger.info("   请手动在浏览器中找到职位选择器，并记录：")
        logger.info("   1. 选择器的类名")
        logger.info("   2. 选择器显示的文本")
        logger.info("   3. 选择器的位置")
        await asyncio.sleep(120)

    except Exception as e:
        logger.error(f"❌ 错误: {str(e)}", exc_info=True)

    finally:
        await automation.cleanup()


if __name__ == "__main__":
    asyncio.run(find_job_selector())
