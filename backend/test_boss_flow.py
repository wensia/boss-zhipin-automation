"""
Boss 直聘自动化流程测试脚本
用于验证页面元素和自动化流程
"""
import asyncio
from playwright.async_api import async_playwright


async def test_boss_login_flow():
    """测试 Boss 直聘登录流程"""
    print("🚀 开始测试 Boss 直聘登录流程...")

    async with async_playwright() as p:
        # 启动浏览器（非无头模式，方便观察）
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
            ]
        )

        # 创建浏览器上下文
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        # 注入反检测脚本
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        # 创建新页面
        page = await context.new_page()

        try:
            # 步骤 1: 访问 Boss 直聘首页
            print("\n📍 步骤 1: 访问 Boss 直聘首页...")
            await page.goto('https://www.zhipin.com/', wait_until='networkidle', timeout=30000)
            print("   ✅ 页面加载成功")

            # 等待页面加载完成
            await asyncio.sleep(2)

            # 步骤 2: 检查登录按钮
            print("\n📍 步骤 2: 检查登录按钮是否存在...")
            login_button_selector = '#header > div.inner.home-inner > div.user-nav > div > a'

            # 尝试查找登录按钮
            login_button = await page.query_selector(login_button_selector)

            if login_button:
                print(f"   ✅ 找到登录按钮: {login_button_selector}")

                # 获取按钮文本
                button_text = await login_button.inner_text()
                print(f"   📝 按钮文本: {button_text}")

                # 步骤 3: 点击登录按钮
                print("\n📍 步骤 3: 点击登录按钮...")
                await login_button.click()
                print("   ✅ 已点击登录按钮")

                # 等待页面跳转
                await asyncio.sleep(3)

                # 获取当前 URL
                current_url = page.url
                print(f"   📝 当前页面 URL: {current_url}")

                # 步骤 4: 检查登录页面元素
                print("\n📍 步骤 4: 检查登录页面元素...")

                # 尝试查找常见的登录元素
                selectors_to_check = [
                    ('登录表单', 'form'),
                    ('手机号输入框', 'input[type="tel"]'),
                    ('密码输入框', 'input[type="password"]'),
                    ('验证码输入框', 'input[placeholder*="验证码"]'),
                    ('扫码登录', '.qrcode'),
                    ('二维码', '.qr-code'),
                    ('登录按钮', 'button[type="submit"]'),
                ]

                for name, selector in selectors_to_check:
                    element = await page.query_selector(selector)
                    if element:
                        print(f"   ✅ 找到元素: {name} ({selector})")
                    else:
                        print(f"   ❌ 未找到元素: {name} ({selector})")

                # 截图保存
                screenshot_path = 'login_page_screenshot.png'
                await page.screenshot(path=screenshot_path, full_page=True)
                print(f"\n📸 已保存登录页面截图: {screenshot_path}")

                # 等待用户观察
                print("\n⏳ 等待 10 秒，请观察登录页面...")
                await asyncio.sleep(10)

            else:
                print(f"   ❌ 未找到登录按钮: {login_button_selector}")
                print("   🔍 尝试查找其他可能的登录元素...")

                # 尝试查找其他可能的登录相关元素
                alternative_selectors = [
                    '.user-nav a',
                    'a[href*="login"]',
                    'button:has-text("登录")',
                    'a:has-text("登录")',
                    '.login-btn',
                    '#loginBtn',
                ]

                for selector in alternative_selectors:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.inner_text()
                        print(f"   ✅ 找到可能的登录元素: {selector} - 文本: {text}")

                # 保存首页截图
                screenshot_path = 'homepage_screenshot.png'
                await page.screenshot(path=screenshot_path, full_page=True)
                print(f"\n📸 已保存首页截图: {screenshot_path}")

                # 输出页面 HTML 结构（部分）
                print("\n📄 页面 header 区域 HTML 结构:")
                header_html = await page.inner_html('#header') if await page.query_selector('#header') else "未找到 header"
                print(header_html[:500] + "..." if len(header_html) > 500 else header_html)

        except Exception as e:
            print(f"\n❌ 测试过程中发生错误: {str(e)}")
            import traceback
            traceback.print_exc()

            # 发生错误时也保存截图
            try:
                await page.screenshot(path='error_screenshot.png', full_page=True)
                print("📸 已保存错误截图: error_screenshot.png")
            except:
                pass

        finally:
            # 关闭浏览器
            print("\n🔚 测试完成，关闭浏览器...")
            await browser.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Boss 直聘自动化流程测试")
    print("=" * 60)
    asyncio.run(test_boss_login_flow())
    print("\n" + "=" * 60)
    print("测试结束")
    print("=" * 60)
