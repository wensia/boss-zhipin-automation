"""
测试脚本：捕捉打招呼限制弹窗的实际结构
用于分析弹窗的DOM结构并优化检测逻辑
"""
import asyncio
import logging
from playwright.async_api import async_playwright
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.boss_automation import BossAutomation

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def capture_limit_dialog():
    """捕捉并分析打招呼限制弹窗"""

    automation = BossAutomation()

    try:
        # 初始化浏览器（显示窗口以便观察）
        await automation.initialize(headless=False)
        logger.info("✅ 浏览器初始化成功")

        # 检查登录状态
        login_result = await automation.check_login_status()
        if not login_result.get('logged_in'):
            logger.error("❌ 未登录，请先登录")
            return

        logger.info(f"✅ 已登录: {login_result.get('user_info', {}).get('showName')}")

        # 导航到推荐页面
        await automation.navigate_to_recommend_page()
        logger.info("✅ 已导航到推荐页面")

        # 等待页面加载
        await asyncio.sleep(3)

        # 获取 iframe
        recommend_frame = None
        for frame in automation.page.frames:
            if frame.name == 'recommendFrame':
                recommend_frame = frame
                break

        if not recommend_frame:
            logger.error("❌ 未找到 recommendFrame")
            return

        logger.info("✅ 找到推荐页面 iframe")

        # 尝试点击第一个候选人的打招呼按钮
        logger.info("🖱️ 尝试触发打招呼...")

        try:
            # 点击第一个候选人
            first_card = recommend_frame.locator('ul.card-list > li:nth-child(1)').first
            await first_card.wait_for(state='visible', timeout=5000)

            name_el = first_card.locator('.name').first
            candidate_name = await name_el.inner_text() if await name_el.count() > 0 else "候选人1"
            logger.info(f"📋 候选人: {candidate_name}")

            await first_card.click()
            await asyncio.sleep(2)

            # 等待简历面板
            await recommend_frame.wait_for_selector('.dialog-lib-resume', timeout=10000)
            logger.info("✅ 简历面板已加载")

            # 查找打招呼按钮
            button_selectors = [
                '.dialog-lib-resume .button-list-wrap button',
                '.dialog-lib-resume .communication button',
                '.resume-right-side .communication button',
            ]

            button = None
            for selector in button_selectors:
                try:
                    btn = recommend_frame.locator(selector).first
                    if await btn.count() > 0 and await btn.is_visible():
                        text = await btn.inner_text()
                        logger.info(f"找到按钮: '{text}'")
                        button = btn
                        break
                except:
                    continue

            if button:
                # 点击打招呼按钮
                await button.click()
                logger.info("✅ 已点击打招呼按钮")

                # 等待几秒，让限制弹窗出现
                logger.info("⏱️ 等待5秒，检查是否出现限制弹窗...")
                await asyncio.sleep(5)

                # 开始检测弹窗（在主页面和 iframe 中都检测）
                logger.info("=" * 80)
                logger.info("🔍 开始分析页面中的弹窗元素...")
                logger.info("=" * 80)

                # 检测位置列表：主页面和 iframe
                frames_to_check = [
                    ("主页面", automation.page),
                    ("recommendFrame", recommend_frame)
                ]

                for frame_name, frame_obj in frames_to_check:
                    logger.info(f"\n{'='*60}")
                    logger.info(f"检测位置: {frame_name}")
                    logger.info(f"{'='*60}")

                    # 方法1：检测用户提供的选择器
                    logger.info("\n[方法1] 检测指定选择器:")
                    selector1 = '#boss-dynamic-dialog-1j94d4cmn > div.boss-popup__wrapper.boss-dialog.boss-dialog__wrapper.business-block-dialog.business-block-wrap.circle > div.boss-popup__content'
                    try:
                        element1 = frame_obj.locator(selector1).first
                        count1 = await element1.count()
                        logger.info(f"  选择器: {selector1}")
                        logger.info(f"  元素数量: {count1}")
                        if count1 > 0:
                            is_visible1 = await element1.is_visible()
                            logger.info(f"  是否可见: {is_visible1}")
                            if is_visible1:
                                content1 = await element1.inner_text()
                                logger.info(f"  内容: {content1[:200]}")
                    except Exception as e:
                        logger.error(f"  检测失败: {e}")

                    # 方法1.5：检测更通用的选择器
                    logger.info("\n[方法1.5] 检测通用选择器:")
                    generic_selectors = [
                        '.business-block-dialog',
                        '.business-block-wrap',
                        '[class*="business-block"]',
                        '[class*="boss-dialog"]',
                        '#boss-dynamic-dialog-1j94d4cmn',
                    ]
                    for sel in generic_selectors:
                        try:
                            elements = frame_obj.locator(sel)
                            count = await elements.count()
                            if count > 0:
                                logger.info(f"  选择器 '{sel}': 找到 {count} 个元素")
                                for i in range(min(count, 3)):
                                    el = elements.nth(i)
                                    is_visible = await el.is_visible()
                                    if is_visible:
                                        try:
                                            text = await el.inner_text()
                                            logger.info(f"    元素 {i+1}: 可见，文本: {text[:100]}")
                                        except:
                                            logger.info(f"    元素 {i+1}: 可见（无法获取文本）")
                        except Exception as e:
                            pass

                    # 方法2：查找所有对话框
                    logger.info("\n[方法2] 查找所有 dialog 元素:")
                    dialogs = await frame_obj.query_selector_all('[class*="dialog"]')
                    logger.info(f"  找到 {len(dialogs)} 个 dialog 元素")
                    for i, dialog in enumerate(dialogs[:10]):  # 只显示前10个
                        try:
                            is_visible = await dialog.is_visible()
                            if is_visible:
                                class_name = await dialog.get_attribute('class')
                                id_attr = await dialog.get_attribute('id')
                                logger.info(f"  Dialog {i+1}:")
                                logger.info(f"    ID: {id_attr}")
                                logger.info(f"    Class: {class_name}")
                                try:
                                    text = await dialog.inner_text()
                                    logger.info(f"    文本: {text[:100]}")
                                except:
                                    pass
                        except:
                            pass

                    # 方法3：查找所有 popup 元素
                    logger.info("\n[方法3] 查找所有 popup 元素:")
                    popups = await frame_obj.query_selector_all('[class*="popup"]')
                    logger.info(f"  找到 {len(popups)} 个 popup 元素")
                    for i, popup in enumerate(popups[:10]):
                        try:
                            is_visible = await popup.is_visible()
                            if is_visible:
                                class_name = await popup.get_attribute('class')
                                id_attr = await popup.get_attribute('id')
                                logger.info(f"  Popup {i+1}:")
                                logger.info(f"    ID: {id_attr}")
                                logger.info(f"    Class: {class_name}")
                                try:
                                    text = await popup.inner_text()
                                    logger.info(f"    文本: {text[:100]}")
                                except:
                                    pass
                        except:
                            pass

                    # 方法4：使用 JavaScript 查找包含特定文本的元素
                    logger.info("\n[方法4] 查找包含限制相关文本的元素:")
                    keywords = ["打招呼", "上限", "限制", "已达", "次数", "明天"]

                    result = await frame_obj.evaluate("""
                        (keywords) => {
                            const elements = [];
                            const allElements = document.querySelectorAll('*');

                            for (const el of allElements) {
                                // 检查元素是否可见
                                const style = window.getComputedStyle(el);
                                if (style.display === 'none' || style.visibility === 'hidden') {
                                    continue;
                                }

                                // 获取元素的文本内容
                                const text = el.textContent || '';

                                // 检查是否包含关键词
                                for (const keyword of keywords) {
                                    if (text.includes(keyword)) {
                                        // 确保不是太大的容器（避免误报）
                                        if (text.length < 500) {
                                            elements.push({
                                                tag: el.tagName,
                                                id: el.id,
                                                className: el.className,
                                                text: text.substring(0, 200),
                                                selector: el.id ? `#${el.id}` : `.${el.className.split(' ')[0]}`
                                            });
                                            break;
                                        }
                                    }
                                }
                            }

                            return elements;
                        }
                    """, keywords)

                    logger.info(f"  找到 {len(result)} 个包含关键词的元素:")
                    for i, el in enumerate(result[:10]):
                        logger.info(f"  元素 {i+1}:")
                        logger.info(f"    标签: {el['tag']}")
                        logger.info(f"    ID: {el['id']}")
                        logger.info(f"    Class: {el['className']}")
                        logger.info(f"    文本: {el['text']}")
                        logger.info(f"    选择器: {el['selector']}")
                        logger.info("")

                # 方法5：截图保存当前页面
                logger.info("\n[方法5] 保存截图:")
                screenshot_path = Path(__file__).parent / "greeting_limit_dialog.png"
                await automation.page.screenshot(path=str(screenshot_path), full_page=True)
                logger.info(f"  截图已保存到: {screenshot_path}")

                logger.info("=" * 80)
                logger.info("✅ 分析完成！")
                logger.info("=" * 80)

                # 保持页面打开以便人工检查
                logger.info("\n⏸️ 保持浏览器打开60秒，以便您检查页面...")
                logger.info("   您可以手动检查弹窗的HTML结构")
                await asyncio.sleep(60)
            else:
                logger.warning("⚠️ 未找到打招呼按钮")

        except Exception as e:
            logger.error(f"❌ 触发打招呼失败: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}", exc_info=True)

    finally:
        # 清理
        try:
            await automation.cleanup()
            logger.info("✅ 清理完成")
        except:
            pass


async def main():
    """主函数"""
    logger.info("=" * 80)
    logger.info("🚀 开始测试打招呼限制弹窗捕捉")
    logger.info("=" * 80)
    logger.info("")
    logger.info("说明：")
    logger.info("  1. 确保已经达到打招呼上限")
    logger.info("  2. 脚本会尝试触发打招呼")
    logger.info("  3. 然后分析页面中的弹窗元素")
    logger.info("  4. 结果将输出到控制台和截图文件")
    logger.info("")
    logger.info("=" * 80)

    await capture_limit_dialog()


if __name__ == "__main__":
    asyncio.run(main())
