"""
简单文本搜索 - 直接查找包含职位文本的元素
"""
import asyncio
import logging
from pathlib import Path
from app.services.boss_automation import BossAutomation

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)


async def simple_text_search():
    """简单文本搜索"""
    automation = BossAutomation()

    try:
        logger.info("=" * 80)
        logger.info("🔍 简单文本搜索 - 查找职位选择器")
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
        logger.info("⏳ 等待15秒让页面完全加载...")
        await asyncio.sleep(15)

        # 截图
        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "simple_01_loaded.png"))
        logger.info("📸 已保存截图")

        # 查找所有可点击的元素
        logger.info("\n" + "=" * 80)
        logger.info("🔍 查找所有可能可点击的元素")
        logger.info("=" * 80)

        all_clickable = await automation.page.evaluate("""
            () => {
                const elements = [];
                const allElems = document.querySelectorAll('*');

                allElems.forEach(elem => {
                    const text = elem.textContent ? elem.textContent.trim() : '';
                    const rect = elem.getBoundingClientRect();
                    const style = window.getComputedStyle(elem);

                    // 收集所有可见且可能可点击的元素
                    if (rect.width > 0 && rect.height > 0 && text.length > 0 && text.length < 300) {
                        // 生成完整路径
                        let path = [];
                        let current = elem;
                        while (current && current.nodeType === Node.ELEMENT_NODE) {
                            let selector = current.nodeName.toLowerCase();
                            if (current.id) {
                                selector = '#' + current.id;
                                path.unshift(selector);
                                break;
                            }
                            if (current.className && typeof current.className === 'string') {
                                const classes = current.className.trim().split(/\\s+/).filter(c => c);
                                if (classes.length > 0) {
                                    selector += '.' + classes.join('.');
                                }
                            }
                            path.unshift(selector);
                            current = current.parentElement;
                        }

                        elements.push({
                            fullPath: path.join(' > '),
                            tagName: elem.tagName,
                            className: typeof elem.className === 'string' ? elem.className : '',
                            text: text.substring(0, 200),
                            cursor: style.cursor,
                            display: style.display,
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

        logger.info(f"\n找到 {len(all_clickable)} 个可见元素")

        # 过滤包含 "新媒体" 或其他职位关键词的元素
        job_related = [
            elem for elem in all_clickable
            if ('新媒体' in elem['text'] or '剪辑' in elem['text'] or
                ('K' in elem['text'] and '_' in elem['text'] and len(elem['text']) > 20))
        ]

        logger.info(f"其中 {len(job_related)} 个包含职位相关信息:")
        for idx, elem in enumerate(job_related[:15], 1):
            logger.info(f"\n元素 {idx}:")
            logger.info(f"  完整路径: {elem['fullPath']}")
            logger.info(f"  标签: {elem['tagName']}")
            logger.info(f"  类名: {elem['className']}")
            logger.info(f"  光标: {elem['cursor']}")
            logger.info(f"  位置: top={elem['position']['top']}, left={elem['position']['left']}, width={elem['position']['width']}, height={elem['position']['height']}")
            logger.info(f"  文本: {elem['text']}")

        # 尝试点击最有可能的元素（位置在100-150之间，宽度>300）
        best_candidates = [
            elem for elem in job_related
            if (elem['position']['top'] >= 100 and elem['position']['top'] <= 150 and
                elem['position']['width'] > 300)
        ]

        logger.info(f"\n\n找到 {len(best_candidates)} 个最佳候选:")
        for idx, candidate in enumerate(best_candidates, 1):
            logger.info(f"\n候选 {idx}:")
            logger.info(f"  完整路径: {candidate['fullPath']}")
            logger.info(f"  文本: {candidate['text']}")
            logger.info(f"  位置: top={candidate['position']['top']}, left={candidate['position']['left']}")

        if best_candidates:
            logger.info("\n" + "=" * 80)
            logger.info("🎯 尝试点击最佳候选")
            logger.info("=" * 80)

            selector = best_candidates[0]['fullPath']
            logger.info(f"使用选择器: {selector}")

            try:
                # 先截图
                await automation.page.screenshot(path=str(SCREENSHOT_DIR / "simple_02_before_click.png"))

                element = await automation.page.query_selector(selector)
                if element:
                    logger.info("✅ 找到元素并点击...")
                    await element.click()
                    await asyncio.sleep(3)

                    # 截图点击后
                    await automation.page.screenshot(path=str(SCREENSHOT_DIR / "simple_03_after_click.png"))
                    logger.info("📸 已保存点击后截图")

                    # 查找下拉列表中的 li 元素
                    logger.info("\n🔍 查找下拉列表...")
                    dropdown_info = await automation.page.evaluate("""
                        () => {
                            const uls = document.querySelectorAll('ul');
                            const dropdownData = [];

                            uls.forEach(ul => {
                                const rect = ul.getBoundingClientRect();
                                if (rect.width > 100 && rect.height > 50) {
                                    const lis = ul.querySelectorAll('li');
                                    const liData = [];

                                    lis.forEach(li => {
                                        liData.push({
                                            value: li.getAttribute('value'),
                                            className: typeof li.className === 'string' ? li.className : '',
                                            text: li.textContent.trim().substring(0, 150),
                                            html: li.outerHTML.substring(0, 200)
                                        });
                                    });

                                    if (liData.length > 0) {
                                        dropdownData.push({
                                            ulClassName: typeof ul.className === 'string' ? ul.className : '',
                                            liCount: liData.length,
                                            items: liData
                                        });
                                    }
                                }
                            });

                            return dropdownData;
                        }
                    """)

                    logger.info(f"\n找到 {len(dropdown_info)} 个下拉列表:")
                    for idx, dropdown in enumerate(dropdown_info, 1):
                        logger.info(f"\n下拉列表 {idx}:")
                        logger.info(f"  ul类名: {dropdown['ulClassName']}")
                        logger.info(f"  li元素数: {dropdown['liCount']}")
                        logger.info(f"\n  职位列表:")
                        for idx2, item in enumerate(dropdown['items'], 1):
                            logger.info(f"\n    职位 {idx2}:")
                            logger.info(f"      value: {item['value']}")
                            logger.info(f"      类名: {item['className']}")
                            logger.info(f"      文本: {item['text']}")
                            logger.info(f"      HTML: {item['html'][:150]}...")

                else:
                    logger.error("❌ 选择器未找到元素")

            except Exception as e:
                logger.error(f"❌ 点击失败: {e}", exc_info=True)

        logger.info("\n⏳ 浏览器将保持打开 120 秒...")
        await asyncio.sleep(120)

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}", exc_info=True)
        try:
            await automation.page.screenshot(path=str(SCREENSHOT_DIR / "simple_error.png"))
        except:
            pass

    finally:
        await automation.cleanup()


if __name__ == "__main__":
    asyncio.run(simple_text_search())
