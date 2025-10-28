"""
反爬虫和反检测工具模块
"""
import random
import asyncio
from typing import Optional
from playwright.async_api import Page


class AntiDetection:
    """反检测工具类"""

    @staticmethod
    def get_random_delay(min_seconds: float = 2.0, max_seconds: float = 5.0) -> float:
        """
        生成随机延迟时间

        Args:
            min_seconds: 最小延迟秒数
            max_seconds: 最大延迟秒数

        Returns:
            随机延迟秒数
        """
        return random.uniform(min_seconds, max_seconds)

    @staticmethod
    async def random_sleep(min_seconds: float = 2.0, max_seconds: float = 5.0):
        """
        随机休眠

        Args:
            min_seconds: 最小延迟秒数
            max_seconds: 最大延迟秒数
        """
        delay = AntiDetection.get_random_delay(min_seconds, max_seconds)
        await asyncio.sleep(delay)

    @staticmethod
    async def inject_anti_detection_script(page: Page):
        """
        注入反检测脚本，隐藏自动化特征

        Args:
            page: Playwright Page 对象
        """
        await page.add_init_script("""
            // 隐藏 webdriver 标志
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // 伪造 plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            // 伪造 languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en']
            });

            // 伪造 Chrome 对象
            window.chrome = {
                runtime: {}
            };

            // 覆盖 permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)

    @staticmethod
    async def simulate_mouse_movement(page: Page):
        """
        模拟鼠标移动

        Args:
            page: Playwright Page 对象
        """
        x = random.randint(100, 800)
        y = random.randint(100, 600)
        await page.mouse.move(x, y)
        await asyncio.sleep(random.uniform(0.1, 0.3))

    @staticmethod
    async def simulate_scroll(page: Page):
        """
        模拟页面滚动

        Args:
            page: Playwright Page 对象
        """
        # 随机滚动方向和距离
        scroll_distance = random.randint(100, 500)
        direction = random.choice(['down', 'up'])

        if direction == 'down':
            await page.evaluate(f'window.scrollBy(0, {scroll_distance})')
        else:
            await page.evaluate(f'window.scrollBy(0, -{scroll_distance})')

        await asyncio.sleep(random.uniform(0.5, 1.5))

    @staticmethod
    async def simulate_human_typing(page: Page, selector: str, text: str):
        """
        模拟人类打字速度

        Args:
            page: Playwright Page 对象
            selector: 输入框选择器
            text: 要输入的文本
        """
        await page.click(selector)
        for char in text:
            await page.type(selector, char, delay=random.uniform(50, 150))

    @staticmethod
    async def check_for_captcha(page: Page) -> bool:
        """
        检查是否出现验证码

        Args:
            page: Playwright Page 对象

        Returns:
            是否检测到验证码
        """
        captcha_selectors = [
            '.geetest_',
            '.nc_',
            '.captcha',
            '#captcha',
            '[class*="verify"]',
            '[id*="verify"]',
        ]

        for selector in captcha_selectors:
            element = await page.query_selector(selector)
            if element:
                return True

        return False

    @staticmethod
    async def check_account_limit(page: Page) -> Optional[str]:
        """
        检查账号是否被限制

        Args:
            page: Playwright Page 对象

        Returns:
            如果被限制，返回限制原因；否则返回 None
        """
        page_content = await page.content()

        limit_keywords = [
            '账号异常',
            '操作频繁',
            '暂时无法使用',
            '请稍后再试',
            '账号被限制',
            '系统繁忙',
        ]

        for keyword in limit_keywords:
            if keyword in page_content:
                return keyword

        return None

    @staticmethod
    async def rest_like_human(seconds: int):
        """
        像人类一样休息

        Args:
            seconds: 休息秒数（实际会有随机波动）
        """
        actual_seconds = seconds + random.uniform(-10, 10)
        actual_seconds = max(5, actual_seconds)  # 至少休息5秒
        await asyncio.sleep(actual_seconds)

    @staticmethod
    def get_random_user_agent() -> str:
        """
        获取随机 User-Agent

        Returns:
            随机的 User-Agent 字符串
        """
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        ]
        return random.choice(user_agents)
