"""
验证简历弹窗和打招呼按钮是否在iframe内
"""
import asyncio
import logging
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def verify_iframe_structure():
    """验证iframe结构和按钮位置"""
    async with async_playwright() as p:
        try:
            logger.info("=" * 80)
            logger.info("🔍 验证iframe结构和按钮位置")
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

            # 导航
            logger.info("📍 导航到推荐牛人页面...")
            await page.goto('https://www.zhipin.com/web/chat/recommend', wait_until='networkidle')
            await asyncio.sleep(3)

            # 列出所有iframe
            logger.info("\n" + "=" * 80)
            logger.info("📋 页面中的所有iframe")
            logger.info("=" * 80)

            all_frames = page.frames
            logger.info(f"总共找到 {len(all_frames)} 个frame (包括主页面)")

            for i, frame in enumerate(all_frames):
                logger.info(f"\nFrame {i}:")
                logger.info(f"  Name: {frame.name}")
                logger.info(f"  URL: {frame.url[:100]}...")

            # 找到recommendFrame并点击候选人
            recommend_frame = None
            for frame in all_frames:
                if frame.name == 'recommendFrame':
                    recommend_frame = frame
                    break

            if not recommend_frame:
                logger.error("❌ 未找到recommendFrame")
                await browser.close()
                return

            logger.info("\n✅ 找到 recommendFrame")

            # 点击第一个候选人
            card = recommend_frame.locator('ul.card-list > li:nth-child(1)').first
            logger.info("🖱️  点击第一个候选人...")
            await card.click()
            await asyncio.sleep(5)  # 等待简历加载

            # 再次列出所有iframe（看是否有新iframe）
            logger.info("\n" + "=" * 80)
            logger.info("📋 点击后的所有iframe")
            logger.info("=" * 80)

            all_frames_after = page.frames
            logger.info(f"现在有 {len(all_frames_after)} 个frame")

            for i, frame in enumerate(all_frames_after):
                logger.info(f"\nFrame {i}:")
                logger.info(f"  Name: {frame.name}")
                logger.info(f"  URL: {frame.url[:100]}...")

            # 在每个frame中查找打招呼按钮
            logger.info("\n" + "=" * 80)
            logger.info("🔍 在每个frame中查找打招呼按钮")
            logger.info("=" * 80)

            for i, frame in enumerate(all_frames_after):
                logger.info(f"\n--- 检查 Frame {i} (Name: {frame.name}) ---")

                try:
                    # 查找包含"打招呼"的按钮
                    buttons_info = await frame.evaluate("""
                        () => {
                            const buttons = Array.from(document.querySelectorAll('button'));
                            return buttons.map((btn, idx) => ({
                                index: idx,
                                text: btn.textContent.trim(),
                                className: btn.className,
                                visible: btn.offsetWidth > 0 && btn.offsetHeight > 0
                            })).filter(b =>
                                b.text.includes('打招呼') ||
                                b.text.includes('立即沟通') ||
                                b.text.includes('继续沟通') ||
                                b.text.includes('发消息')
                            );
                        }
                    """)

                    if buttons_info:
                        logger.info(f"  ✅ 找到 {len(buttons_info)} 个相关按钮:")
                        for btn_info in buttons_info:
                            logger.info(f"    - '{btn_info['text']}' (可见: {btn_info['visible']})")
                            logger.info(f"      类名: {btn_info['className']}")
                    else:
                        logger.info("  ❌ 未找到相关按钮")

                    # 查找对话框相关元素
                    dialog_count = await frame.locator('[class*="dialog"]').count()
                    popup_count = await frame.locator('[class*="popup"]').count()
                    resume_count = await frame.locator('[class*="resume"]').count()

                    logger.info(f"  Dialog元素: {dialog_count}")
                    logger.info(f"  Popup元素: {popup_count}")
                    logger.info(f"  Resume元素: {resume_count}")

                except Exception as e:
                    logger.info(f"  ❌ 检查失败: {e}")

            # 使用用户提供的选择器测试
            logger.info("\n" + "=" * 80)
            logger.info("🔍 测试用户提供的选择器路径")
            logger.info("=" * 80)

            # 用户提供的完整选择器（去掉动态ID）
            test_selectors = [
                # 完整路径（基于用户提供的选择器，但使用通配符替代动态ID）
                '[id*="boss-dynamic-dialog"] .boss-dialog__wrapper.dialog-lib-resume button',
                '.boss-dialog__wrapper.dialog-lib-resume .button-list-wrap button',
                '.dialog-lib-resume .communication .button-list-wrap button',
                '.resume-right-side .communication button',

                # 更简化的选择器
                '[class*="boss-popup"] button',
                '[class*="dialog-lib-resume"] button',
            ]

            for selector in test_selectors:
                logger.info(f"\n测试选择器: {selector}")

                # 在主页面测试
                try:
                    count_main = await page.locator(selector).count()
                    logger.info(f"  主页面: 找到 {count_main} 个元素")
                    if count_main > 0:
                        for i in range(min(count_main, 3)):
                            el = page.locator(selector).nth(i)
                            try:
                                text = await el.inner_text()
                                visible = await el.is_visible()
                                logger.info(f"    元素{i+1}: '{text}' (可见: {visible})")
                            except:
                                pass
                except Exception as e:
                    logger.info(f"  主页面: 错误 - {e}")

                # 在recommendFrame测试
                try:
                    count_frame = await recommend_frame.locator(selector).count()
                    logger.info(f"  recommendFrame: 找到 {count_frame} 个元素")
                    if count_frame > 0:
                        for i in range(min(count_frame, 3)):
                            el = recommend_frame.locator(selector).nth(i)
                            try:
                                text = await el.inner_text()
                                visible = await el.is_visible()
                                logger.info(f"    元素{i+1}: '{text}' (可见: {visible})")
                            except:
                                pass
                except Exception as e:
                    logger.info(f"  recommendFrame: 错误 - {e}")

            # 保持浏览器打开
            logger.info("\n" + "=" * 80)
            logger.info("✅ 验证完成！浏览器将保持打开60秒以便手动检查")
            logger.info("=" * 80)
            await asyncio.sleep(60)

            await browser.close()

        except Exception as e:
            logger.error(f"❌ 验证失败: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(verify_iframe_structure())
