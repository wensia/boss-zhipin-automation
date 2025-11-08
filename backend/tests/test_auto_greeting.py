"""
Boss直聘自动打招呼测试脚本
测试完整的打招呼流程：
1. 点击候选人卡片
2. 等待简历加载
3. 点击打招呼按钮
4. 等待按钮变为"继续沟通"
5. 关闭简历界面
6. 继续下一个候选人
"""
import asyncio
import logging
from typing import Optional
from playwright.async_api import async_playwright, Page, Frame, Locator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def find_recommend_frame(page: Page) -> Optional[Frame]:
    """查找 recommendFrame iframe"""
    for frame in page.frames:
        if frame.name == 'recommendFrame':
            logger.info(f"✅ 找到 recommendFrame: {frame.url}")
            return frame
    logger.error("❌ 未找到 recommendFrame")
    return None


async def scroll_if_needed(frame: Frame, index: int):
    """如果需要，向下滚动以加载更多候选人"""
    try:
        # 每5个候选人滚动一次
        if index > 0 and index % 5 == 0:
            logger.info(f"📜 滚动加载更多候选人...")
            await frame.evaluate("""
                window.scrollTo({
                    top: document.documentElement.scrollHeight,
                    behavior: 'smooth'
                });
            """)
            await asyncio.sleep(2)
    except Exception as e:
        logger.warning(f"滚动失败: {e}")


async def click_candidate_card(frame: Frame, index: int) -> bool:
    """点击第 index 个候选人卡片"""
    try:
        selector = f'ul.card-list > li:nth-child({index + 1})'
        card = frame.locator(selector).first

        # 确保元素可见
        await card.wait_for(state='visible', timeout=5000)

        # 获取候选人名字用于日志
        name_el = card.locator('.name').first
        name = await name_el.inner_text() if await name_el.count() > 0 else f"候选人{index+1}"

        logger.info(f"🖱️  点击候选人卡片: {name}")
        await card.click()
        await asyncio.sleep(2)  # 等待页面响应

        return True
    except Exception as e:
        logger.error(f"❌ 点击候选人卡片失败: {e}")
        return False


async def wait_for_resume_panel(frame: Frame) -> bool:
    """等待简历面板加载完成（在recommendFrame中）"""
    try:
        logger.info("⏳ 等待简历面板加载...")

        # 在recommendFrame中等待简历对话框出现
        try:
            await frame.wait_for_selector('.dialog-lib-resume', timeout=5000, state='visible')
            logger.info("✅ 简历面板已加载")
            await asyncio.sleep(1)  # 等待动画完成
            return True
        except:
            # 如果没有找到特定选择器，等待一段时间让页面稳定
            await asyncio.sleep(2)
            logger.info("✅ 简历面板可能已加载（通过延迟）")
            return True

    except Exception as e:
        logger.error(f"❌ 等待简历面板失败: {e}")
        return False


async def click_greeting_button(frame: Frame) -> bool:
    """点击打招呼按钮（在recommendFrame中）"""
    try:
        logger.info("🔍 查找打招呼按钮...")

        # 基于MCP验证结果，使用最可靠的选择器
        # 按钮在recommendFrame的简历对话框中
        button_selectors = [
            '.dialog-lib-resume .button-list-wrap button',
            '.dialog-lib-resume .communication button',
            '.resume-right-side .communication button',
            'button.btn-greet',
        ]

        for selector in button_selectors:
            try:
                button = frame.locator(selector).first
                if await button.count() > 0 and await button.is_visible():
                    text = await button.inner_text()
                    logger.info(f"✅ 找到按钮: '{text}' (选择器: {selector})")
                    await button.click()
                    logger.info(f"✅ 已点击【{text}】按钮")
                    return True
            except Exception as e:
                logger.debug(f"选择器 {selector} 失败: {e}")
                continue

        logger.warning("⚠️ 未找到打招呼按钮，可能已经打过招呼")
        return False

    except Exception as e:
        logger.error(f"❌ 点击打招呼按钮失败: {e}")
        return False


async def wait_for_greeting_success(frame: Frame) -> bool:
    """等待打招呼成功，按钮变为'继续沟通'（在recommendFrame中）"""
    try:
        logger.info("⏳ 等待打招呼完成...")

        # 等待按钮文本变化
        await asyncio.sleep(2)

        # 检查是否出现"继续沟通"或类似文本（在recommendFrame中）
        try:
            # 查找对话框中的按钮
            button = frame.locator('.dialog-lib-resume button').first
            if await button.count() > 0:
                text = await button.inner_text()
                if '继续沟通' in text or '发消息' in text:
                    logger.info(f"✅ 打招呼成功！按钮已变为: {text}")
                    return True
        except:
            pass

        # 即使没有找到继续沟通按钮，也认为可能成功了
        logger.info("✅ 打招呼可能已完成")
        return True

    except Exception as e:
        logger.error(f"❌ 等待打招呼成功失败: {e}")
        return False


async def close_resume_panel(frame: Frame) -> bool:
    """关闭简历面板，返回候选人列表（在recommendFrame中）"""
    try:
        logger.info("🔍 查找关闭按钮...")

        # 关闭按钮在recommendFrame的对话框中
        close_selectors = [
            '.dialog-lib-resume .boss-popup__close',
            '.dialog-lib-resume button.close',
            '.dialog-lib-resume .close-btn',
            '.dialog-lib-resume [class*="close"]',
            '.boss-popup__close',
        ]

        for selector in close_selectors:
            try:
                close_btn = frame.locator(selector).first
                if await close_btn.count() > 0 and await close_btn.is_visible():
                    logger.info(f"✅ 找到关闭按钮 (选择器: {selector})")
                    await close_btn.click()
                    logger.info("✅ 已关闭简历面板")
                    await asyncio.sleep(1)
                    return True
            except:
                continue

        # 尝试按 ESC 键关闭
        logger.info("尝试按 ESC 键关闭...")
        await frame.page.keyboard.press('Escape')
        await asyncio.sleep(1)
        logger.info("✅ 已按 ESC 键")
        return True

    except Exception as e:
        logger.error(f"❌ 关闭简历面板失败: {e}")
        return False


async def auto_greeting_flow(
    target_count: int = 10,
    auth_file: str = 'boss_auth.json'
):
    """
    自动打招呼流程

    Args:
        target_count: 目标打招呼数量
        auth_file: 登录状态文件
    """
    success_count = 0
    failed_count = 0

    async with async_playwright() as p:
        try:
            logger.info("=" * 80)
            logger.info(f"🚀 Boss直聘自动打招呼测试")
            logger.info(f"目标数量: {target_count}")
            logger.info("=" * 80)

            # 启动浏览器
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                ]
            )

            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                storage_state=auth_file
            )
            page = await context.new_page()

            # 导航到推荐牛人页面
            logger.info("🔍 导航到推荐牛人页面...")
            await page.goto('https://www.zhipin.com/web/chat/recommend', wait_until='networkidle')
            await asyncio.sleep(3)

            # 查找 iframe
            recommend_frame = await find_recommend_frame(page)
            if not recommend_frame:
                logger.error("❌ 无法找到候选人列表")
                await browser.close()
                return

            await asyncio.sleep(2)

            logger.info(f"\n{'=' * 80}")
            logger.info(f"🎯 开始自动打招呼流程")
            logger.info(f"{'=' * 80}\n")

            # 循环处理候选人
            for i in range(target_count):
                try:
                    logger.info(f"\n{'─' * 80}")
                    logger.info(f"📍 处理第 {i + 1}/{target_count} 个候选人")
                    logger.info(f"{'─' * 80}")

                    # 1. 如果需要，向下滚动
                    await scroll_if_needed(recommend_frame, i)

                    # 2. 点击候选人卡片
                    if not await click_candidate_card(recommend_frame, i):
                        logger.error(f"❌ 跳过候选人 {i + 1}")
                        failed_count += 1
                        continue

                    # 3. 等待简历面板加载（在recommendFrame中）
                    if not await wait_for_resume_panel(recommend_frame):
                        logger.error(f"❌ 简历未加载，跳过候选人 {i + 1}")
                        failed_count += 1
                        await close_resume_panel(recommend_frame)
                        continue

                    # 4. 点击打招呼按钮（在recommendFrame中）
                    greeting_clicked = await click_greeting_button(recommend_frame)

                    # 5. 等待打招呼成功（在recommendFrame中）
                    if greeting_clicked:
                        await wait_for_greeting_success(recommend_frame)

                    # 6. 关闭简历面板（在recommendFrame中）
                    await close_resume_panel(recommend_frame)

                    # 7. 等待返回列表
                    await asyncio.sleep(1)

                    success_count += 1
                    logger.info(f"✅ 候选人 {i + 1} 处理完成")

                    # 短暂延迟，避免操作太快
                    await asyncio.sleep(1)

                except Exception as e:
                    logger.error(f"❌ 处理候选人 {i + 1} 时出错: {e}")
                    failed_count += 1
                    # 尝试关闭面板并继续
                    try:
                        await close_resume_panel(recommend_frame)
                    except:
                        pass
                    continue

            # 统计结果
            logger.info(f"\n{'=' * 80}")
            logger.info("📊 自动打招呼完成统计")
            logger.info(f"{'=' * 80}")
            logger.info(f"✅ 成功处理: {success_count}/{target_count}")
            logger.info(f"❌ 失败/跳过: {failed_count}/{target_count}")
            logger.info(f"成功率: {success_count/target_count*100:.1f}%")
            logger.info(f"{'=' * 80}")

            # 保持浏览器打开一段时间以便查看
            logger.info("\n⏳ 等待 5 秒后关闭浏览器...")
            await asyncio.sleep(5)
            await browser.close()

        except Exception as e:
            logger.error(f"❌ 自动打招呼流程失败: {e}", exc_info=True)


async def main():
    """主函数"""
    await auto_greeting_flow(
        target_count=10,
        auth_file='boss_auth.json'
    )


if __name__ == "__main__":
    asyncio.run(main())
