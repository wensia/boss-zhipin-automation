"""
根据截图查找职位选择器
等待更长时间，使用多种方法定位元素
"""
import asyncio
import logging
from pathlib import Path
from app.services.boss_automation import BossAutomation

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)


async def find_job_selector_precisely():
    """精确查找职位选择器"""
    automation = BossAutomation()

    try:
        logger.info("=" * 80)
        logger.info("🎯 根据截图精确查找职位选择器")
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

        # 等待更长时间让页面完全加载
        logger.info("⏳ 等待页面完全加载（10秒）...")
        await asyncio.sleep(10)

        current_url = automation.page.url
        logger.info(f"✅ 当前URL: {current_url}")

        # 截图1：初始状态
        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "precise_01_initial.png"))
        logger.info("📸 已保存初始截图")

        # 方法1: 查找包含职位信息的所有元素
        logger.info("\n" + "=" * 80)
        logger.info("🔍 方法1: 查找所有包含下拉箭头的元素")
        logger.info("=" * 80)

        dropdown_elements = await automation.page.evaluate("""
            () => {
                const elements = [];
                const allElems = document.querySelectorAll('*');

                allElems.forEach(elem => {
                    const text = elem.textContent.trim();
                    const rect = elem.getBoundingClientRect();
                    const style = window.getComputedStyle(elem);

                    // 查找在页面中央顶部、宽度较大的可点击元素
                    if (rect.width > 200 && rect.height > 20 && rect.height < 100 &&
                        rect.top >= 80 && rect.top < 150 &&
                        rect.left > 400 && rect.left < 1000 &&
                        text.length > 10) {

                        // 生成CSS选择器
                        let selector = elem.tagName.toLowerCase();
                        if (elem.id) {
                            selector = '#' + elem.id;
                        } else if (elem.className && typeof elem.className === 'string') {
                            const classes = elem.className.trim().split(/\\s+/).filter(c => c);
                            if (classes.length > 0) {
                                selector += '.' + classes.join('.');
                            }
                        }

                        elements.push({
                            tagName: elem.tagName,
                            className: typeof elem.className === 'string' ? elem.className : '',
                            id: elem.id || '',
                            text: text.substring(0, 150),
                            selector: selector,
                            cursor: style.cursor,
                            position: {
                                top: Math.round(rect.top),
                                left: Math.round(rect.left),
                                width: Math.round(rect.width),
                                height: Math.round(rect.height)
                            }
                        });
                    }
                });

                return elements;
            }
        """)

        logger.info(f"\n找到 {len(dropdown_elements)} 个可能的下拉元素:")
        for idx, elem in enumerate(dropdown_elements, 1):
            logger.info(f"\n元素 {idx}:")
            logger.info(f"  标签: {elem['tagName']}")
            logger.info(f"  类名: {elem['className']}")
            logger.info(f"  ID: {elem['id']}")
            logger.info(f"  选择器: {elem['selector']}")
            logger.info(f"  光标: {elem['cursor']}")
            logger.info(f"  位置: top={elem['position']['top']}, left={elem['position']['left']}, width={elem['position']['width']}")
            logger.info(f"  文本: {elem['text']}")

        # 方法2: 查找包含 K (薪资) 的元素
        logger.info("\n" + "=" * 80)
        logger.info("🔍 方法2: 查找包含薪资信息(K)的元素")
        logger.info("=" * 80)

        salary_elements = await automation.page.evaluate("""
            () => {
                const elements = [];
                const allElems = document.querySelectorAll('*');

                allElems.forEach(elem => {
                    const text = elem.textContent.trim();
                    const rect = elem.getBoundingClientRect();

                    // 查找包含 "K" 且可能是职位选择器的元素
                    if (text.includes('K') && text.includes('-') &&
                        rect.width > 150 && rect.top < 200) {

                        elements.push({
                            tagName: elem.tagName,
                            className: typeof elem.className === 'string' ? elem.className : '',
                            text: text.substring(0, 150),
                            position: {
                                top: Math.round(rect.top),
                                left: Math.round(rect.left),
                                width: Math.round(rect.width)
                            }
                        });
                    }
                });

                return elements;
            }
        """)

        logger.info(f"\n找到 {len(salary_elements)} 个包含薪资的元素:")
        for idx, elem in enumerate(salary_elements, 1):
            logger.info(f"\n元素 {idx}:")
            logger.info(f"  标签: {elem['tagName']}")
            logger.info(f"  类名: {elem['className']}")
            logger.info(f"  位置: top={elem['position']['top']}, left={elem['position']['left']}")
            logger.info(f"  文本: {elem['text']}")

        # 方法3: 生成完整的CSS路径
        logger.info("\n" + "=" * 80)
        logger.info("🔍 方法3: 为可能的职位选择器生成完整CSS路径")
        logger.info("=" * 80)

        job_selector_info = await automation.page.evaluate("""
            () => {
                function getFullPath(elem) {
                    const path = [];
                    while (elem && elem.nodeType === Node.ELEMENT_NODE) {
                        let selector = elem.nodeName.toLowerCase();

                        if (elem.id) {
                            selector = '#' + elem.id;
                            path.unshift(selector);
                            break;
                        }

                        if (elem.className && typeof elem.className === 'string') {
                            const classes = elem.className.trim().split(/\\s+/).filter(c => c);
                            if (classes.length > 0) {
                                selector += '.' + classes.join('.');
                            }
                        }

                        path.unshift(selector);
                        elem = elem.parentElement;
                    }

                    return path.join(' > ');
                }

                // 查找包含 "K" 和 城市信息的元素（很可能是职位选择器）
                const candidates = [];
                const allElems = document.querySelectorAll('*');

                allElems.forEach(elem => {
                    const text = elem.textContent.trim();
                    const rect = elem.getBoundingClientRect();

                    if (text.includes('K') && text.includes('_') &&
                        rect.width > 200 && rect.top > 80 && rect.top < 150) {

                        candidates.push({
                            fullPath: getFullPath(elem),
                            tagName: elem.tagName,
                            className: typeof elem.className === 'string' ? elem.className : '',
                            text: text.substring(0, 150),
                            outerHTML: elem.outerHTML.substring(0, 300),
                            position: {
                                top: Math.round(rect.top),
                                left: Math.round(rect.left),
                                width: Math.round(rect.width)
                            }
                        });
                    }
                });

                return candidates;
            }
        """)

        logger.info(f"\n找到 {len(job_selector_info)} 个职位选择器候选:")
        for idx, candidate in enumerate(job_selector_info, 1):
            logger.info(f"\n候选 {idx}:")
            logger.info(f"  完整路径: {candidate['fullPath']}")
            logger.info(f"  标签: {candidate['tagName']}")
            logger.info(f"  类名: {candidate['className']}")
            logger.info(f"  位置: top={candidate['position']['top']}, left={candidate['position']['left']}, width={candidate['position']['width']}")
            logger.info(f"  文本: {candidate['text']}")
            logger.info(f"  HTML: {candidate['outerHTML'][:200]}...")

        # 如果找到候选，尝试点击第一个
        if job_selector_info and len(job_selector_info) > 0:
            logger.info("\n" + "=" * 80)
            logger.info("🎯 尝试点击第一个候选职位选择器")
            logger.info("=" * 80)

            first_candidate = job_selector_info[0]
            selector = first_candidate['fullPath']

            logger.info(f"使用选择器: {selector}")

            try:
                element = await automation.page.query_selector(selector)
                if element:
                    logger.info("✅ 找到元素，准备点击...")

                    # 截图2：点击前
                    await automation.page.screenshot(path=str(SCREENSHOT_DIR / "precise_02_before_click.png"))

                    await element.click()
                    await asyncio.sleep(2)

                    # 截图3：点击后
                    await automation.page.screenshot(path=str(SCREENSHOT_DIR / "precise_03_after_click.png"))
                    logger.info("📸 已保存点击前后截图")

                    # 查找下拉列表
                    logger.info("\n🔍 查找下拉列表...")
                    dropdown_list = await automation.page.evaluate("""
                        () => {
                            const lists = [];
                            const ulElements = document.querySelectorAll('ul');

                            ulElements.forEach(ul => {
                                const rect = ul.getBoundingClientRect();
                                if (rect.width > 100 && rect.height > 50) {
                                    const liElements = ul.querySelectorAll('li');
                                    if (liElements.length > 0) {
                                        lists.push({
                                            liCount: liElements.length,
                                            className: typeof ul.className === 'string' ? ul.className : '',
                                            position: {
                                                top: Math.round(rect.top),
                                                left: Math.round(rect.left)
                                            }
                                        });
                                    }
                                }
                            });

                            return lists;
                        }
                    """)

                    logger.info(f"找到 {len(dropdown_list)} 个可能的下拉列表:")
                    for idx, lst in enumerate(dropdown_list, 1):
                        logger.info(f"\n  列表 {idx}:")
                        logger.info(f"    li元素数: {lst['liCount']}")
                        logger.info(f"    类名: {lst['className']}")
                        logger.info(f"    位置: top={lst['position']['top']}, left={lst['position']['left']}")

                else:
                    logger.error("❌ 选择器未找到元素")
            except Exception as e:
                logger.error(f"❌ 点击失败: {e}")

        # 截图4：最终状态
        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "precise_04_final.png"))
        logger.info("\n📸 已保存最终截图")

        # 保持浏览器打开
        logger.info("\n" + "=" * 80)
        logger.info("✅ 分析完成！")
        logger.info("=" * 80)
        logger.info("📸 所有截图已保存到: screenshots/")
        logger.info("\n⏳ 浏览器将保持打开 120 秒...")
        await asyncio.sleep(120)

    except Exception as e:
        logger.error(f"❌ 分析失败: {e}", exc_info=True)
        try:
            await automation.page.screenshot(path=str(SCREENSHOT_DIR / "precise_error.png"))
        except:
            pass

    finally:
        await automation.cleanup()


if __name__ == "__main__":
    asyncio.run(find_job_selector_precisely())
