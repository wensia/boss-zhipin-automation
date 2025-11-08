"""
使用MCP探索打招呼按钮的DOM结构
根据用户提供的选择器分析正确的定位方法
"""
import asyncio
import logging
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def explore_greeting_button():
    """探索打招呼按钮的DOM结构"""
    async with async_playwright() as p:
        try:
            logger.info("=" * 80)
            logger.info("🔍 探索打招呼按钮DOM结构")
            logger.info("=" * 80)

            browser = await p.chromium.launch(
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )

            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                storage_state='boss_auth.json'
            )
            page = await context.new_page()

            # 导航并点击第一个候选人
            logger.info("📍 导航到推荐牛人页面...")
            await page.goto('https://www.zhipin.com/web/chat/recommend', wait_until='networkidle')
            await asyncio.sleep(3)

            # 找到iframe并点击第一个候选人
            recommend_frame = None
            for frame in page.frames:
                if frame.name == 'recommendFrame':
                    recommend_frame = frame
                    break

            if recommend_frame:
                logger.info("✅ 找到 recommendFrame")
                card = recommend_frame.locator('ul.card-list > li:nth-child(1)').first
                logger.info("🖱️  点击第一个候选人...")
                await card.click()

                # 等待简历面板完全加载
                logger.info("⏳ 等待简历面板加载...")

                # 等待对话框出现
                try:
                    await page.wait_for_selector('[class*="boss-popup"]', timeout=10000, state='visible')
                    logger.info("✅ 检测到对话框")
                except:
                    logger.warning("⚠️ 未检测到标准对话框，继续探索...")

                await asyncio.sleep(3)

                logger.info("\n" + "=" * 80)
                logger.info("🔍 分析简历对话框结构")
                logger.info("=" * 80)

                # 1. 查找所有可能的对话框容器
                boss_popups = await page.locator('[class*="boss-popup"]').all()
                logger.info(f"找到 {len(boss_popups)} 个boss-popup元素")

                # 2. 查找所有dialog
                dialogs = await page.locator('[class*="dialog"]').all()
                logger.info(f"找到 {len(dialogs)} 个dialog元素")

                # 2. 查找resume相关的dialog
                resume_dialogs = await page.locator('[class*="resume"]').all()
                logger.info(f"找到 {len(resume_dialogs)} 个resume相关元素")

                # 3. 查找button-list-wrap
                button_wraps = await page.locator('.button-list-wrap').all()
                logger.info(f"找到 {len(button_wraps)} 个button-list-wrap")

                if button_wraps:
                    for i, wrap in enumerate(button_wraps):
                        logger.info(f"\n--- button-list-wrap #{i+1} ---")
                        buttons = await wrap.locator('button').all()
                        logger.info(f"  包含 {len(buttons)} 个button")
                        for j, btn in enumerate(buttons):
                            text = await btn.inner_text()
                            is_visible = await btn.is_visible()
                            logger.info(f"  Button {j+1}: '{text}' (可见: {is_visible})")

                # 4. 查找communication区域
                logger.info("\n🔍 查找communication区域...")
                comm_areas = await page.locator('.communication').all()
                logger.info(f"找到 {len(comm_areas)} 个communication区域")

                # 5. 尝试用户提供的选择器模式（不含动态ID）
                logger.info("\n🔍 测试各种选择器...")

                selectors_to_test = [
                    # 基于类名的通用选择器
                    '.dialog-lib-resume .button-list-wrap button',
                    '.resume-right-side .button-list-wrap button',
                    '.communication .button-list-wrap button',

                    # 更具体的路径
                    '.boss-dialog__wrapper.dialog-lib-resume .communication button',
                    '[class*="dialog-lib-resume"] [class*="button-list-wrap"] button',

                    # 基于文本
                    'button:has-text("打招呼")',
                    'button:has-text("立即沟通")',
                ]

                for selector in selectors_to_test:
                    try:
                        elements = await page.locator(selector).all()
                        logger.info(f"\n选择器: {selector}")
                        logger.info(f"  找到 {len(elements)} 个元素")

                        if elements:
                            for i, el in enumerate(elements):
                                try:
                                    text = await el.inner_text()
                                    is_visible = await el.is_visible()
                                    logger.info(f"  元素 {i+1}: '{text}' (可见: {is_visible})")
                                except:
                                    pass
                    except Exception as e:
                        logger.info(f"  ❌ 错误: {e}")

                # 6. 使用evaluate获取更详细的DOM信息
                logger.info("\n" + "=" * 80)
                logger.info("🔍 获取详细DOM结构")
                logger.info("=" * 80)

                dom_info = await page.evaluate("""
                    () => {
                        const results = [];

                        // 查找所有包含"打招呼"或"立即沟通"的按钮
                        const buttons = Array.from(document.querySelectorAll('button'));

                        buttons.forEach((btn, index) => {
                            const text = btn.textContent.trim();
                            if (text.includes('打招呼') || text.includes('立即沟通') || text.includes('继续沟通')) {
                                const rect = btn.getBoundingClientRect();
                                results.push({
                                    index: index,
                                    text: text,
                                    className: btn.className,
                                    id: btn.id,
                                    visible: rect.width > 0 && rect.height > 0,
                                    position: {
                                        top: rect.top,
                                        left: rect.left,
                                        width: rect.width,
                                        height: rect.height
                                    },
                                    parentClasses: btn.parentElement ? btn.parentElement.className : '',
                                    path: (() => {
                                        let el = btn;
                                        let path = [];
                                        while (el && el.tagName !== 'BODY' && path.length < 5) {
                                            let selector = el.tagName.toLowerCase();
                                            if (el.className) {
                                                const classes = el.className.split(' ').slice(0, 2).join('.');
                                                selector += '.' + classes;
                                            }
                                            path.unshift(selector);
                                            el = el.parentElement;
                                        }
                                        return path.join(' > ');
                                    })()
                                });
                            }
                        });

                        return results;
                    }
                """)

                logger.info(f"找到 {len(dom_info)} 个相关按钮:")
                for i, info in enumerate(dom_info):
                    logger.info(f"\n按钮 #{i+1}:")
                    logger.info(f"  文本: {info['text']}")
                    logger.info(f"  可见: {info['visible']}")
                    logger.info(f"  类名: {info['className']}")
                    logger.info(f"  父元素类: {info['parentClasses']}")
                    logger.info(f"  路径: {info['path']}")

                # 保持浏览器打开以便手动检查
                logger.info("\n" + "=" * 80)
                logger.info("✅ 探索完成！浏览器将保持打开60秒以便手动检查")
                logger.info("=" * 80)
                await asyncio.sleep(60)

            await browser.close()

        except Exception as e:
            logger.error(f"❌ 探索失败: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(explore_greeting_button())
