"""
候选人列表结构探索测试
用于分析Boss直聘推荐候选人列表的DOM结构、交互逻辑和滚动行为
"""
import asyncio
import logging
from playwright.async_api import async_playwright

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def explore_candidate_list():
    """探索候选人列表的结构和交互"""

    async with async_playwright() as p:
        # 启动浏览器（显示窗口以便观察）
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
            ]
        )

        # 加载已保存的登录状态
        context_options = {
            'viewport': {'width': 1920, 'height': 1080},
            'storage_state': 'boss_auth.json'  # 使用保存的登录状态
        }
        context = await browser.new_context(**context_options)
        page = await context.new_page()

        try:
            logger.info("=" * 80)
            logger.info("步骤 1: 导航到推荐牛人页面")
            logger.info("=" * 80)

            await page.goto("https://www.zhipin.com/web/chat/recommend", wait_until='networkidle')
            await asyncio.sleep(5)

            logger.info(f"✅ 当前URL: {page.url}")

            # ================================================================
            logger.info("\n" + "=" * 80)
            logger.info("步骤 2: 检测 iframe 结构")
            logger.info("=" * 80)

            frames = page.frames
            logger.info(f"📊 页面包含 {len(frames)} 个 frame")

            recommend_frame = None
            for idx, frame in enumerate(frames):
                logger.info(f"\nFrame {idx}:")
                logger.info(f"  - Name: {frame.name}")
                logger.info(f"  - URL: {frame.url}")

                if frame.name == 'recommendFrame':
                    recommend_frame = frame
                    logger.info(f"  ✅ 这是 recommendFrame（候选人列表iframe）")

            if not recommend_frame:
                logger.error("❌ 未找到 recommendFrame，无法继续")
                return

            # ================================================================
            logger.info("\n" + "=" * 80)
            logger.info("步骤 3: 分析候选人列表元素结构")
            logger.info("=" * 80)

            # 等待候选人列表加载
            await asyncio.sleep(3)

            # 测试不同的选择器
            selectors_to_test = [
                "#recommend-list",
                "#recommend-list > div",
                "#recommend-list > div > ul",
                "#recommend-list > div > ul > li",  # 直接查找 li 元素
                ".card-list",
                ".card-list > li",
                "ul.card-list > li",
                ".geek-list",
                ".geek-item",
                "ul.geek-list",
                "li.geek-item",
            ]

            for selector in selectors_to_test:
                try:
                    elements = await recommend_frame.query_selector_all(selector)
                    logger.info(f"✅ '{selector}' - 找到 {len(elements)} 个元素")

                    if len(elements) > 0:
                        # 获取第一个元素的信息
                        first_element = elements[0]
                        tag_name = await first_element.evaluate("el => el.tagName")
                        class_name = await first_element.evaluate("el => el.className")
                        logger.info(f"   第一个元素: <{tag_name}> class=\"{class_name}\"")

                except Exception as e:
                    logger.warning(f"⚠️  '{selector}' - 未找到或出错: {e}")

            # ================================================================
            logger.info("\n" + "=" * 80)
            logger.info("步骤 4: 获取候选人卡片结构")
            logger.info("=" * 80)

            # 尝试获取候选人卡片
            candidate_cards = await recommend_frame.query_selector_all("ul.card-list > li")

            if not candidate_cards:
                candidate_cards = await recommend_frame.query_selector_all(".card-list > li")

            if not candidate_cards:
                candidate_cards = await recommend_frame.query_selector_all("li.geek-item")

            if not candidate_cards:
                candidate_cards = await recommend_frame.query_selector_all(".geek-item")

            logger.info(f"📋 找到 {len(candidate_cards)} 个候选人卡片")

            if len(candidate_cards) > 0:
                logger.info("\n分析第一个候选人卡片的结构：")
                first_card = candidate_cards[0]

                # 获取卡片的HTML结构
                card_html = await first_card.evaluate("""
                    el => {
                        return {
                            tag: el.tagName,
                            className: el.className,
                            innerHTML: el.innerHTML.substring(0, 500) + '...',
                            attributes: Array.from(el.attributes).map(attr => ({
                                name: attr.name,
                                value: attr.value
                            }))
                        }
                    }
                """)

                logger.info(f"  标签: {card_html['tag']}")
                logger.info(f"  类名: {card_html['className']}")
                logger.info(f"  属性: {card_html['attributes']}")

                # 尝试提取候选人信息
                candidate_info = await first_card.evaluate("""
                    el => {
                        const getName = () => {
                            const nameEl = el.querySelector('.geek-name, .name, h3');
                            return nameEl ? nameEl.textContent.trim() : null;
                        };

                        const getPosition = () => {
                            const posEl = el.querySelector('.geek-position, .position, .job-title');
                            return posEl ? posEl.textContent.trim() : null;
                        };

                        const getCompany = () => {
                            const companyEl = el.querySelector('.geek-company, .company');
                            return companyEl ? companyEl.textContent.trim() : null;
                        };

                        const getActiveTime = () => {
                            const timeEl = el.querySelector('.geek-active-time, .active-time, .time');
                            return timeEl ? timeEl.textContent.trim() : null;
                        };

                        return {
                            name: getName(),
                            position: getPosition(),
                            company: getCompany(),
                            activeTime: getActiveTime(),
                            allText: el.textContent.substring(0, 200)
                        };
                    }
                """)

                logger.info(f"\n  候选人信息:")
                logger.info(f"    姓名: {candidate_info.get('name', 'N/A')}")
                logger.info(f"    职位: {candidate_info.get('position', 'N/A')}")
                logger.info(f"    公司: {candidate_info.get('company', 'N/A')}")
                logger.info(f"    活跃时间: {candidate_info.get('activeTime', 'N/A')}")
                logger.info(f"    完整文本: {candidate_info.get('allText', 'N/A')[:100]}...")

            # ================================================================
            logger.info("\n" + "=" * 80)
            logger.info("步骤 5: 测试点击候选人卡片")
            logger.info("=" * 80)

            if len(candidate_cards) > 0:
                logger.info("🖱️  准备点击第一个候选人卡片...")

                # 记录点击前的状态
                before_click = {
                    'url': page.url,
                    'frame_count': len(page.frames)
                }
                logger.info(f"点击前状态: URL={before_click['url']}, Frames={before_click['frame_count']}")

                # 点击卡片
                await candidate_cards[0].click()
                await asyncio.sleep(3)

                # 记录点击后的状态
                after_click = {
                    'url': page.url,
                    'frame_count': len(page.frames)
                }
                logger.info(f"点击后状态: URL={after_click['url']}, Frames={after_click['frame_count']}")

                # 检查是否打开了新的详情页
                if after_click['url'] != before_click['url']:
                    logger.info("✅ URL发生变化，打开了候选人详情页")
                    # 返回列表页
                    await page.go_back()
                    await asyncio.sleep(2)
                else:
                    logger.info("ℹ️  URL未变化，在当前页面展开了详情")
                    # 尝试关闭详情面板（如果有关闭按钮）
                    try:
                        close_button = await page.query_selector('.close, .close-btn, .icon-close')
                        if close_button:
                            await close_button.click()
                            await asyncio.sleep(1)
                            logger.info("✅ 已关闭详情面板")
                    except:
                        logger.info("ℹ️  未找到关闭按钮，继续执行")

            # ================================================================
            logger.info("\n" + "=" * 80)
            logger.info("步骤 6: 分析滚动容器和滚动逻辑")
            logger.info("=" * 80)

            # 重新获取iframe（返回后可能需要重新查找）
            recommend_frame = None
            for frame in page.frames:
                if frame.name == 'recommendFrame':
                    recommend_frame = frame
                    break

            if recommend_frame:
                # 查找滚动容器
                scroll_info = await recommend_frame.evaluate("""
                    () => {
                        // 可能的滚动容器选择器
                        const containers = [
                            '#recommend-list',
                            '#recommend-list > div',
                            '.geek-list-container',
                            'ul.geek-list',
                            document.querySelector('#recommend-list')?.parentElement
                        ];

                        const results = [];

                        for (const selector of containers) {
                            if (typeof selector === 'string') {
                                const el = document.querySelector(selector);
                                if (el) {
                                    results.push({
                                        selector: selector,
                                        scrollHeight: el.scrollHeight,
                                        clientHeight: el.clientHeight,
                                        scrollTop: el.scrollTop,
                                        isScrollable: el.scrollHeight > el.clientHeight,
                                        overflowY: window.getComputedStyle(el).overflowY
                                    });
                                }
                            } else if (selector) {
                                results.push({
                                    selector: 'parentElement',
                                    scrollHeight: selector.scrollHeight,
                                    clientHeight: selector.clientHeight,
                                    scrollTop: selector.scrollTop,
                                    isScrollable: selector.scrollHeight > selector.clientHeight,
                                    overflowY: window.getComputedStyle(selector).overflowY
                                });
                            }
                        }

                        return results;
                    }
                """)

                logger.info("📜 滚动容器信息：")
                for info in scroll_info:
                    logger.info(f"\n  容器: {info['selector']}")
                    logger.info(f"    scrollHeight: {info['scrollHeight']}px")
                    logger.info(f"    clientHeight: {info['clientHeight']}px")
                    logger.info(f"    scrollTop: {info['scrollTop']}px")
                    logger.info(f"    可滚动: {info['isScrollable']}")
                    logger.info(f"    overflow-y: {info['overflowY']}")

                # ================================================================
                logger.info("\n" + "=" * 80)
                logger.info("步骤 7: 测试滚动加载更多候选人")
                logger.info("=" * 80)

                # 获取当前候选人数量
                initial_count = len(await recommend_frame.query_selector_all("ul.card-list > li"))
                logger.info(f"📊 初始候选人数量: {initial_count}")

                # 执行滚动 - 注意：在iframe中需要滚动iframe的document
                logger.info("🔄 开始滚动...")
                for i in range(3):
                    await recommend_frame.evaluate("""
                        () => {
                            // 在iframe中，滚动整个document
                            window.scrollTo({
                                top: document.documentElement.scrollHeight,
                                behavior: 'smooth'
                            });
                        }
                    """)
                    logger.info(f"  滚动次数: {i + 1}")
                    await asyncio.sleep(2)

                # 获取滚动后的候选人数量
                final_count = len(await recommend_frame.query_selector_all("ul.card-list > li"))
                logger.info(f"📊 滚动后候选人数量: {final_count}")
                logger.info(f"📈 新增候选人: {final_count - initial_count}")

            # ================================================================
            logger.info("\n" + "=" * 80)
            logger.info("步骤 8: 生成完整的候选人列表数据结构")
            logger.info("=" * 80)

            if recommend_frame:
                candidates_data = await recommend_frame.evaluate("""
                    () => {
                        const cards = document.querySelectorAll('ul.card-list > li');
                        const candidates = [];

                        cards.forEach((card, index) => {
                            candidates.push({
                                index: index,
                                selector: `ul.card-list > li:nth-child(${index + 1})`,
                                text: card.textContent.substring(0, 100),
                                className: card.className,
                                dataAttributes: Array.from(card.attributes)
                                    .filter(attr => attr.name.startsWith('data-'))
                                    .map(attr => ({name: attr.name, value: attr.value}))
                            });
                        });

                        return {
                            total: candidates.length,
                            candidates: candidates.slice(0, 5) // 只返回前5个作为示例
                        };
                    }
                """)

                logger.info(f"📊 候选人总数: {candidates_data['total']}")
                logger.info(f"\n前5个候选人示例:")
                for candidate in candidates_data['candidates']:
                    logger.info(f"\n  候选人 {candidate['index']}:")
                    logger.info(f"    选择器: {candidate['selector']}")
                    logger.info(f"    类名: {candidate['className']}")
                    logger.info(f"    文本: {candidate['text']}...")
                    logger.info(f"    数据属性: {candidate['dataAttributes']}")

            logger.info("\n" + "=" * 80)
            logger.info("✅ 探索完成！按任意键继续...")
            logger.info("=" * 80)

            # 等待用户观察
            await asyncio.sleep(30)

        except Exception as e:
            logger.error(f"❌ 探索过程中出错: {e}", exc_info=True)

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(explore_candidate_list())
