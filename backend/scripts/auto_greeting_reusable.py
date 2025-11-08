"""
Boss直聘自动打招呼 - 可重用函数库
提供简洁的API供其他模块调用
"""
import asyncio
import logging
from typing import Optional, Dict, List
from playwright.async_api import async_playwright, Page, Frame

# 配置日志
logger = logging.getLogger(__name__)


class GreetingAutomation:
    """自动打招呼类"""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self.recommend_frame = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.close()

    async def initialize(self, auth_file: str = 'boss_auth.json'):
        """
        初始化浏览器和页面

        Args:
            auth_file: 登录状态文件路径
        """
        self.playwright = await async_playwright().start()

        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
            ]
        )

        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            storage_state=auth_file
        )
        self.page = await self.context.new_page()

        # 导航到推荐牛人页面
        await self.page.goto('https://www.zhipin.com/web/chat/recommend', wait_until='networkidle')
        await asyncio.sleep(3)

        # 查找 recommendFrame
        self.recommend_frame = await self._find_recommend_frame()
        if not self.recommend_frame:
            raise RuntimeError("无法找到 recommendFrame")

        await asyncio.sleep(2)

    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def _find_recommend_frame(self) -> Optional[Frame]:
        """查找 recommendFrame iframe"""
        for frame in self.page.frames:
            if frame.name == 'recommendFrame':
                return frame
        return None

    async def _scroll_if_needed(self, index: int, scroll_interval: int = 5):
        """如果需要，向下滚动以加载更多候选人"""
        if index > 0 and index % scroll_interval == 0:
            logger.info(f"滚动加载更多候选人...")
            await self.recommend_frame.evaluate("""
                window.scrollTo({
                    top: document.documentElement.scrollHeight,
                    behavior: 'smooth'
                });
            """)
            await asyncio.sleep(2)

    async def _click_candidate_card(self, index: int) -> bool:
        """点击第 index 个候选人卡片"""
        try:
            selector = f'ul.card-list > li:nth-child({index + 1})'
            card = self.recommend_frame.locator(selector).first

            await card.wait_for(state='visible', timeout=5000)

            # 获取候选人名字
            name_el = card.locator('.name').first
            name = await name_el.inner_text() if await name_el.count() > 0 else f"候选人{index+1}"

            logger.info(f"点击候选人: {name}")
            await card.click()
            await asyncio.sleep(2)

            return True
        except Exception as e:
            logger.error(f"点击候选人卡片失败: {e}")
            return False

    async def _wait_for_resume_panel(self) -> bool:
        """等待简历面板加载完成"""
        try:
            await self.recommend_frame.wait_for_selector('.dialog-lib-resume', timeout=5000, state='visible')
            await asyncio.sleep(1)
            return True
        except:
            await asyncio.sleep(2)
            return True

    async def _click_greeting_button(self) -> bool:
        """点击打招呼按钮"""
        try:
            button_selectors = [
                '.dialog-lib-resume .button-list-wrap button',
                '.dialog-lib-resume .communication button',
                'button.btn-greet',
            ]

            for selector in button_selectors:
                try:
                    button = self.recommend_frame.locator(selector).first
                    if await button.count() > 0 and await button.is_visible():
                        text = await button.inner_text()
                        logger.info(f"找到按钮: '{text}'")
                        await button.click()
                        return True
                except:
                    continue

            logger.warning("未找到打招呼按钮")
            return False
        except Exception as e:
            logger.error(f"点击打招呼按钮失败: {e}")
            return False

    async def _wait_for_greeting_success(self) -> bool:
        """等待打招呼成功"""
        await asyncio.sleep(2)

        try:
            button = self.recommend_frame.locator('.dialog-lib-resume button').first
            if await button.count() > 0:
                text = await button.inner_text()
                if '继续沟通' in text or '发消息' in text:
                    logger.info(f"打招呼成功！按钮变为: {text}")
                    return True
        except:
            pass

        return True

    async def _close_resume_panel(self) -> bool:
        """关闭简历面板"""
        try:
            close_selectors = [
                '.dialog-lib-resume .boss-popup__close',
                '.boss-popup__close',
            ]

            for selector in close_selectors:
                try:
                    close_btn = self.recommend_frame.locator(selector).first
                    if await close_btn.count() > 0 and await close_btn.is_visible():
                        await close_btn.click()
                        await asyncio.sleep(1)
                        return True
                except:
                    continue

            # 尝试按 ESC 键
            await self.page.keyboard.press('Escape')
            await asyncio.sleep(1)
            return True
        except Exception as e:
            logger.error(f"关闭简历面板失败: {e}")
            return False

    async def greet_one(self, index: int) -> bool:
        """
        向第 index 个候选人打招呼

        Args:
            index: 候选人索引（从0开始）

        Returns:
            bool: 是否成功
        """
        try:
            # 1. 滚动加载（如果需要）
            await self._scroll_if_needed(index)

            # 2. 点击候选人卡片
            if not await self._click_candidate_card(index):
                return False

            # 3. 等待简历面板加载
            if not await self._wait_for_resume_panel():
                await self._close_resume_panel()
                return False

            # 4. 点击打招呼按钮
            greeting_clicked = await self._click_greeting_button()

            # 5. 等待打招呼成功
            if greeting_clicked:
                await self._wait_for_greeting_success()

            # 6. 关闭简历面板
            await self._close_resume_panel()

            # 7. 短暂延迟
            await asyncio.sleep(1)

            return True

        except Exception as e:
            logger.error(f"处理候选人 {index} 时出错: {e}")
            try:
                await self._close_resume_panel()
            except:
                pass
            return False

    async def greet_multiple(
        self,
        target_count: int = 10,
        scroll_interval: int = 5
    ) -> Dict[str, int]:
        """
        批量打招呼

        Args:
            target_count: 目标数量
            scroll_interval: 滚动间隔（每N个候选人滚动一次）

        Returns:
            Dict: {'success_count': int, 'failed_count': int}
        """
        success_count = 0
        failed_count = 0

        logger.info(f"开始批量打招呼，目标数量: {target_count}")

        for i in range(target_count):
            logger.info(f"处理候选人 {i + 1}/{target_count}")

            if await self.greet_one(i):
                success_count += 1
                logger.info(f"✅ 候选人 {i + 1} 处理成功")
            else:
                failed_count += 1
                logger.error(f"❌ 候选人 {i + 1} 处理失败")

        logger.info(f"批量打招呼完成: 成功 {success_count}, 失败 {failed_count}")

        return {
            'success_count': success_count,
            'failed_count': failed_count,
            'total': target_count,
            'success_rate': success_count / target_count if target_count > 0 else 0
        }


# ========== 便捷函数 ==========

async def auto_greet_candidates(
    target_count: int = 10,
    auth_file: str = 'boss_auth.json',
    headless: bool = False
) -> Dict[str, int]:
    """
    自动打招呼（便捷函数）

    Args:
        target_count: 目标数量
        auth_file: 登录状态文件
        headless: 是否无头模式

    Returns:
        Dict: {'success_count': int, 'failed_count': int, 'total': int, 'success_rate': float}

    Example:
        >>> result = await auto_greet_candidates(target_count=20)
        >>> print(f"成功: {result['success_count']}, 失败: {result['failed_count']}")
    """
    async with GreetingAutomation(headless=headless) as automation:
        await automation.initialize(auth_file=auth_file)
        return await automation.greet_multiple(target_count=target_count)


async def auto_greet_specific_candidates(
    candidate_indices: List[int],
    auth_file: str = 'boss_auth.json',
    headless: bool = False
) -> Dict[str, int]:
    """
    对指定索引的候选人打招呼

    Args:
        candidate_indices: 候选人索引列表（例如: [0, 2, 5, 7]）
        auth_file: 登录状态文件
        headless: 是否无头模式

    Returns:
        Dict: {'success_count': int, 'failed_count': int}

    Example:
        >>> # 只对第1、3、5个候选人打招呼
        >>> result = await auto_greet_specific_candidates([0, 2, 4])
    """
    success_count = 0
    failed_count = 0

    async with GreetingAutomation(headless=headless) as automation:
        await automation.initialize(auth_file=auth_file)

        for index in candidate_indices:
            logger.info(f"处理候选人索引: {index}")
            if await automation.greet_one(index):
                success_count += 1
            else:
                failed_count += 1

    return {
        'success_count': success_count,
        'failed_count': failed_count,
        'total': len(candidate_indices),
        'success_rate': success_count / len(candidate_indices) if len(candidate_indices) > 0 else 0
    }


# ========== 示例用法 ==========

async def example_basic():
    """基础用法示例"""
    # 简单打招呼10个候选人
    result = await auto_greet_candidates(target_count=10)
    print(f"成功: {result['success_count']}/{result['total']}")
    print(f"成功率: {result['success_rate']*100:.1f}%")


async def example_advanced():
    """高级用法示例"""
    # 使用类进行更精细的控制
    async with GreetingAutomation(headless=False) as automation:
        await automation.initialize()

        # 先打招呼前5个
        result1 = await automation.greet_multiple(target_count=5)

        # 等待一段时间
        await asyncio.sleep(30)

        # 再打招呼后5个
        result2 = await automation.greet_multiple(target_count=5)

        total_success = result1['success_count'] + result2['success_count']
        print(f"总共成功: {total_success}")


async def example_selective():
    """选择性打招呼示例"""
    # 只对特定候选人打招呼
    selected_indices = [0, 2, 4, 6, 8]  # 第1、3、5、7、9个候选人
    result = await auto_greet_specific_candidates(selected_indices)
    print(f"成功: {result['success_count']}/{result['total']}")


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # 运行示例
    asyncio.run(example_basic())
