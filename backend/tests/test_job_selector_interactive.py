"""
交互式职位选择器测试
使用 Playwright 手动测试职位选择器，并保存截图
"""
import asyncio
import logging
from pathlib import Path
from app.services.boss_automation import BossAutomation

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建截图目录
SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)


async def take_screenshot(page, name: str):
    """保存截图"""
    screenshot_path = SCREENSHOT_DIR / f"{name}.png"
    await page.screenshot(path=str(screenshot_path))
    logger.info(f"📸 截图已保存: {screenshot_path}")


async def test_job_selector_interactive():
    """交互式测试职位选择器"""
    automation = BossAutomation()

    try:
        logger.info("=" * 80)
        logger.info("🧪 交互式测试：职位选择器")
        logger.info("=" * 80)

        # 步骤 1: 初始化浏览器（显示窗口）
        logger.info("\n📍 步骤 1: 初始化浏览器")
        init_success = await automation.initialize(headless=False)
        if not init_success:
            logger.error("❌ 浏览器初始化失败")
            return

        logger.info("✅ 浏览器初始化成功")
        await asyncio.sleep(2)

        # 步骤 2: 检查登录状态
        logger.info("\n📍 步骤 2: 检查登录状态")
        login_status = await automation.check_login_status()

        if not login_status.get('logged_in'):
            logger.error("❌ 未登录，测试终止")
            return

        logger.info("✅ 已登录")

        # 步骤 3: 导航到推荐页面
        logger.info("\n📍 步骤 3: 导航到推荐页面")
        nav_result = await automation.navigate_to_recommend_page()
        await asyncio.sleep(3)

        current_url = automation.page.url
        logger.info(f"✅ 当前URL: {current_url}")

        # 截图 1: 推荐页面初始状态
        await take_screenshot(automation.page, "01_recommend_page_initial")

        # 步骤 4: 检查页面元素
        logger.info("\n" + "=" * 80)
        logger.info("📍 步骤 4: 检查页面元素")
        logger.info("=" * 80)

        # 检查 headerWrap
        header_exists = await automation.page.evaluate("""
            () => {
                const header = document.querySelector('#headerWrap');
                console.log('headerWrap:', header);
                return !!header;
            }
        """)
        logger.info(f"#headerWrap 存在: {header_exists}")

        # 检查所有可能的职位选择器
        selectors_to_check = [
            "#headerWrap > div > div > div.ui-dropmenu.ui-dropmenu-label-arrow.ui-dropmenu-drop-arrow.job-selecter-wrap > div.ui-dropmenu-label",
            ".job-selecter-wrap .ui-dropmenu-label",
            ".job-selecter-wrap",
            ".ui-dropmenu",
            "#headerWrap .ui-dropmenu",
        ]

        found_selector = None
        for selector in selectors_to_check:
            exists = await automation.page.evaluate(f"""
                () => {{
                    const elem = document.querySelector('{selector}');
                    console.log('Selector "{selector}":', elem);
                    return !!elem;
                }}
            """)
            logger.info(f"选择器 '{selector}' 存在: {exists}")
            if exists and not found_selector:
                found_selector = selector

        if not found_selector:
            logger.error("❌ 未找到任何职位选择器")

            # 打印 headerWrap 的完整 HTML
            header_html = await automation.page.evaluate("""
                () => {
                    const header = document.querySelector('#headerWrap');
                    return header ? header.innerHTML : 'not found';
                }
            """)
            logger.info("\n" + "=" * 80)
            logger.info("📄 headerWrap 完整HTML:")
            logger.info("=" * 80)
            logger.info(header_html[:2000])  # 打印前2000个字符

            await take_screenshot(automation.page, "02_no_selector_found")
            logger.info("\n⏳ 保持浏览器打开 60 秒供您手动检查...")
            await asyncio.sleep(60)
            return

        logger.info(f"\n✅ 找到职位选择器: {found_selector}")

        # 步骤 5: 尝试点击职位选择器
        logger.info("\n" + "=" * 80)
        logger.info("📍 步骤 5: 点击职位选择器")
        logger.info("=" * 80)

        # 使用找到的选择器
        trigger_element = await automation.page.query_selector(found_selector)
        if not trigger_element:
            logger.error("❌ 无法获取触发器元素")
            return

        # 截图 2: 点击前
        await take_screenshot(automation.page, "03_before_click")

        # 点击触发器
        logger.info("👆 点击职位选择器...")
        await trigger_element.click()
        await asyncio.sleep(2)  # 等待下拉菜单展开

        # 截图 3: 点击后
        await take_screenshot(automation.page, "04_after_click")

        # 步骤 6: 查找下拉列表
        logger.info("\n" + "=" * 80)
        logger.info("📍 步骤 6: 查找下拉列表")
        logger.info("=" * 80)

        # 检查下拉菜单是否出现
        dropdown_selectors = [
            "#headerWrap > div > div > div.ui-dropmenu.ui-dropmenu-visible.ui-dropmenu-label-arrow.ui-dropmenu-drop-arrow.job-selecter-wrap.expanding > div.ui-dropmenu-list > ul",
            ".ui-dropmenu.expanding .ui-dropmenu-list ul",
            ".job-selecter-wrap.expanding .ui-dropmenu-list ul",
            ".ui-dropmenu-list ul",
            "#headerWrap .ui-dropmenu-list ul",
        ]

        found_list_selector = None
        for selector in dropdown_selectors:
            exists = await automation.page.evaluate(f"""
                () => {{
                    const elem = document.querySelector('{selector}');
                    console.log('List selector "{selector}":', elem);
                    return !!elem;
                }}
            """)
            logger.info(f"列表选择器 '{selector}' 存在: {exists}")
            if exists and not found_list_selector:
                found_list_selector = selector

        if not found_list_selector:
            logger.error("❌ 未找到下拉列表")

            # 打印展开后的 job-selecter-wrap HTML
            dropdown_html = await automation.page.evaluate("""
                () => {
                    const dropdown = document.querySelector('.job-selecter-wrap');
                    return dropdown ? dropdown.outerHTML : 'not found';
                }
            """)
            logger.info("\n" + "=" * 80)
            logger.info("📄 job-selecter-wrap HTML (点击后):")
            logger.info("=" * 80)
            logger.info(dropdown_html[:2000])

            await take_screenshot(automation.page, "05_no_dropdown_found")
            logger.info("\n⏳ 保持浏览器打开 60 秒供您手动检查...")
            await asyncio.sleep(60)
            return

        logger.info(f"\n✅ 找到下拉列表: {found_list_selector}")

        # 步骤 7: 获取职位列表
        logger.info("\n" + "=" * 80)
        logger.info("📍 步骤 7: 获取职位列表")
        logger.info("=" * 80)

        list_element = await automation.page.query_selector(found_list_selector)
        if not list_element:
            logger.error("❌ 无法获取列表元素")
            return

        # 获取所有 li 元素
        all_li = await list_element.query_selector_all("li")
        logger.info(f"📋 找到 {len(all_li)} 个 li 元素")

        # 遍历并打印每个 li 的信息
        jobs = []
        for idx, li in enumerate(all_li):
            # 获取 outerHTML
            html = await li.evaluate("el => el.outerHTML")
            logger.info(f"\n--- li 元素 {idx + 1} ---")
            logger.info(html[:200])

            # 获取属性
            value = await li.get_attribute("value")
            class_name = await li.get_attribute("class")
            data_v = await li.get_attribute("data-v-11890623")

            logger.info(f"value: {value}")
            logger.info(f"class: {class_name}")
            logger.info(f"data-v-11890623: {data_v}")

            # 获取文本内容
            text = await li.text_content()
            logger.info(f"text: {text.strip()[:100]}...")

            if value:
                jobs.append({
                    'value': value,
                    'label': text.strip()
                })

        logger.info(f"\n✅ 成功提取 {len(jobs)} 个职位")
        for idx, job in enumerate(jobs, 1):
            logger.info(f"\n职位 {idx}:")
            logger.info(f"  value: {job['value']}")
            logger.info(f"  label: {job['label'][:100]}...")

        # 截图 4: 展开的下拉列表
        await take_screenshot(automation.page, "06_dropdown_list")

        # 保持浏览器打开供检查
        logger.info("\n" + "=" * 80)
        logger.info("✅ 测试完成！")
        logger.info("=" * 80)
        logger.info(f"📸 所有截图已保存到: {SCREENSHOT_DIR}")
        logger.info("\n⏳ 浏览器将保持打开 60 秒供您检查...")
        await asyncio.sleep(60)

    except Exception as e:
        logger.error(f"\n❌ 测试失败: {str(e)}", exc_info=True)
        try:
            await take_screenshot(automation.page, "99_error_screenshot")
        except:
            pass

    finally:
        logger.info("\n🧹 清理资源...")
        await automation.cleanup()
        logger.info("✅ 测试结束\n")


if __name__ == "__main__":
    asyncio.run(test_job_selector_interactive())
