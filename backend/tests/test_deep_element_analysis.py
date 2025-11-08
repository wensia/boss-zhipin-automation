"""
深度页面元素分析 - 查找职位选择器的真实位置
使用多种方法分析页面结构
"""
import asyncio
import logging
from pathlib import Path
from app.services.boss_automation import BossAutomation

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)


async def deep_analysis():
    """深度分析页面元素"""
    automation = BossAutomation()

    try:
        logger.info("=" * 80)
        logger.info("🔬 深度页面元素分析")
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

        current_url = automation.page.url
        logger.info(f"✅ 当前URL: {current_url}")

        # 截图1：初始页面
        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "analysis_01_initial.png"))
        logger.info("📸 已保存初始页面截图")

        # 分析 1: 检查页面加载状态
        logger.info("\n" + "=" * 80)
        logger.info("📊 分析 1: 页面加载状态")
        logger.info("=" * 80)

        page_info = await automation.page.evaluate("""
            () => {
                return {
                    readyState: document.readyState,
                    title: document.title,
                    url: window.location.href,
                    bodyExists: !!document.body,
                    bodyChildren: document.body ? document.body.children.length : 0
                };
            }
        """)

        for key, value in page_info.items():
            logger.info(f"  {key}: {value}")

        # 分析 2: 查找所有包含 "header" 的元素
        logger.info("\n" + "=" * 80)
        logger.info("📊 分析 2: 查找所有包含 'header' 的元素")
        logger.info("=" * 80)

        header_elements = await automation.page.evaluate("""
            () => {
                const elements = [];
                const allElems = document.querySelectorAll('*');

                allElems.forEach(elem => {
                    const id = elem.id || '';
                    const className = elem.className || '';

                    if (id.toLowerCase().includes('header') ||
                        (typeof className === 'string' && className.toLowerCase().includes('header'))) {

                        const rect = elem.getBoundingClientRect();
                        elements.push({
                            tagName: elem.tagName,
                            id: id,
                            className: typeof className === 'string' ? className : '',
                            text: elem.textContent.trim().substring(0, 100),
                            visible: rect.width > 0 && rect.height > 0,
                            position: {
                                top: rect.top,
                                left: rect.left,
                                width: rect.width,
                                height: rect.height
                            },
                            childrenCount: elem.children.length
                        });
                    }
                });

                return elements;
            }
        """)

        logger.info(f"\n找到 {len(header_elements)} 个包含 'header' 的元素:")
        for idx, elem in enumerate(header_elements, 1):
            logger.info(f"\n元素 {idx}:")
            logger.info(f"  标签: {elem['tagName']}")
            logger.info(f"  ID: {elem['id']}")
            logger.info(f"  类名: {elem['className']}")
            logger.info(f"  可见: {elem['visible']}")
            logger.info(f"  位置: top={elem['position']['top']:.0f}, left={elem['position']['left']:.0f}")
            logger.info(f"  子元素数: {elem['childrenCount']}")
            logger.info(f"  文本: {elem['text'][:80]}...")

        # 分析 3: 查找页面顶部（y < 200）的所有交互元素
        logger.info("\n" + "=" * 80)
        logger.info("📊 分析 3: 页面顶部的交互元素")
        logger.info("=" * 80)

        top_interactive = await automation.page.evaluate("""
            () => {
                const elements = [];
                const allElems = document.querySelectorAll('*');

                allElems.forEach(elem => {
                    const rect = elem.getBoundingClientRect();
                    const style = window.getComputedStyle(elem);

                    // 只查找顶部200px、可见、可能可点击的元素
                    if (rect.top >= 0 && rect.top < 200 &&
                        rect.width > 30 && rect.height > 15 &&
                        (style.cursor === 'pointer' ||
                         elem.onclick !== null ||
                         elem.tagName === 'BUTTON' ||
                         elem.tagName === 'A' ||
                         elem.getAttribute('role') === 'button')) {

                        elements.push({
                            tagName: elem.tagName,
                            id: elem.id || '',
                            className: typeof elem.className === 'string' ? elem.className : '',
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

                // 按 top 位置排序
                elements.sort((a, b) => a.position.top - b.position.top);
                return elements;
            }
        """)

        logger.info(f"\n找到 {len(top_interactive)} 个顶部交互元素:")
        for idx, elem in enumerate(top_interactive[:20], 1):
            logger.info(f"\n元素 {idx}:")
            logger.info(f"  标签: {elem['tagName']}")
            logger.info(f"  ID: {elem['id']}")
            logger.info(f"  类名: {elem['className']}")
            logger.info(f"  光标: {elem['cursor']}")
            logger.info(f"  位置: top={elem['position']['top']:.1f}, left={elem['position']['left']:.1f}, width={elem['position']['width']:.1f}")
            logger.info(f"  文本: {elem['text']}")

        # 分析 4: 查找所有包含 "dropdown" 或 "menu" 的元素
        logger.info("\n" + "=" * 80)
        logger.info("📊 分析 4: 查找下拉菜单/选择器元素")
        logger.info("=" * 80)

        dropdown_elements = await automation.page.evaluate("""
            () => {
                const elements = [];
                const allElems = document.querySelectorAll('*');

                const keywords = ['dropdown', 'dropmenu', 'select', 'picker', 'menu', 'job', '职位'];

                allElems.forEach(elem => {
                    const id = elem.id || '';
                    const className = typeof elem.className === 'string' ? elem.className : '';
                    const text = elem.textContent.trim();

                    let matched = false;
                    keywords.forEach(keyword => {
                        if (id.toLowerCase().includes(keyword) ||
                            className.toLowerCase().includes(keyword) ||
                            text.includes(keyword)) {
                            matched = true;
                        }
                    });

                    if (matched) {
                        const rect = elem.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0 && rect.top < 300) {
                            elements.push({
                                tagName: elem.tagName,
                                id: id,
                                className: className,
                                text: text.substring(0, 100),
                                position: {
                                    top: rect.top,
                                    left: rect.left,
                                    width: rect.width,
                                    height: rect.height
                                },
                                childrenCount: elem.children.length
                            });
                        }
                    }
                });

                return elements;
            }
        """)

        logger.info(f"\n找到 {len(dropdown_elements)} 个可能的下拉菜单元素:")
        for idx, elem in enumerate(dropdown_elements[:15], 1):
            logger.info(f"\n元素 {idx}:")
            logger.info(f"  标签: {elem['tagName']}")
            logger.info(f"  ID: {elem['id']}")
            logger.info(f"  类名: {elem['className']}")
            logger.info(f"  位置: top={elem['position']['top']:.1f}, left={elem['position']['left']:.1f}")
            logger.info(f"  子元素数: {elem['childrenCount']}")
            logger.info(f"  文本: {elem['text']}")

        # 分析 5: 生成完整的 DOM 选择器路径
        logger.info("\n" + "=" * 80)
        logger.info("📊 分析 5: 为可疑元素生成选择器路径")
        logger.info("=" * 80)

        # 找到包含"职位"文本且在顶部的元素
        job_selector_candidates = await automation.page.evaluate("""
            () => {
                function getSelector(elem) {
                    if (elem.id) {
                        return '#' + elem.id;
                    }

                    let path = [];
                    while (elem && elem.nodeType === Node.ELEMENT_NODE) {
                        let selector = elem.nodeName.toLowerCase();

                        if (elem.className && typeof elem.className === 'string') {
                            const classes = elem.className.trim().split(/\\s+/).filter(c => c);
                            if (classes.length > 0) {
                                selector += '.' + classes.join('.');
                            }
                        }

                        path.unshift(selector);

                        if (elem.id) {
                            path[0] = '#' + elem.id;
                            break;
                        }

                        elem = elem.parentElement;
                    }

                    return path.join(' > ');
                }

                const candidates = [];
                const allElems = document.querySelectorAll('*');

                allElems.forEach(elem => {
                    const text = elem.textContent.trim();
                    const rect = elem.getBoundingClientRect();

                    // 查找包含职位信息且在顶部的元素
                    if (text && (text.includes('职位') || text.includes('招聘')) &&
                        rect.top >= 0 && rect.top < 200 &&
                        rect.width > 50 && rect.height > 20) {

                        candidates.push({
                            selector: getSelector(elem),
                            tagName: elem.tagName,
                            text: text.substring(0, 100),
                            className: typeof elem.className === 'string' ? elem.className : '',
                            position: {
                                top: rect.top,
                                left: rect.left
                            }
                        });
                    }
                });

                return candidates;
            }
        """)

        logger.info(f"\n找到 {len(job_selector_candidates)} 个职位选择器候选:")
        for idx, candidate in enumerate(job_selector_candidates, 1):
            logger.info(f"\n候选 {idx}:")
            logger.info(f"  选择器: {candidate['selector']}")
            logger.info(f"  标签: {candidate['tagName']}")
            logger.info(f"  类名: {candidate['className']}")
            logger.info(f"  位置: top={candidate['position']['top']:.1f}, left={candidate['position']['left']:.1f}")
            logger.info(f"  文本: {candidate['text']}")

        # 截图2：分析完成
        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "analysis_02_complete.png"))
        logger.info("\n📸 已保存分析完成截图")

        # 保持浏览器打开
        logger.info("\n" + "=" * 80)
        logger.info("✅ 分析完成！")
        logger.info("=" * 80)
        logger.info("📸 截图已保存到: screenshots/")
        logger.info("\n⏳ 浏览器将保持打开 120 秒...")
        logger.info("   请手动查看页面并找到职位选择器")
        await asyncio.sleep(120)

    except Exception as e:
        logger.error(f"❌ 分析失败: {e}", exc_info=True)
        try:
            await automation.page.screenshot(path=str(SCREENSHOT_DIR / "analysis_error.png"))
        except:
            pass

    finally:
        await automation.cleanup()


if __name__ == "__main__":
    asyncio.run(deep_analysis())
