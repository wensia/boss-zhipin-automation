"""
测试职位选择器功能 V2
探索推荐页面的实际DOM结构
"""
import asyncio
import logging
from app.services.boss_automation import BossAutomation

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_job_selector_v2():
    """测试职位选择器 V2 - 探索页面结构"""
    automation = BossAutomation()

    try:
        logger.info("=" * 80)
        logger.info("🧪 测试：探索推荐页面职位选择器结构")
        logger.info("=" * 80)

        # 步骤 1: 初始化浏览器
        logger.info("\n📍 步骤 1: 初始化浏览器（headless=False）")
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
        logger.info(f"   用户: {login_status.get('user_info', {}).get('name', '未知')}")

        # 步骤 3: 导航到推荐页面（使用正确的URL）
        logger.info("\n📍 步骤 3: 导航到推荐页面")

        # 使用 navigate_to_recommend_page 方法
        nav_result = await automation.navigate_to_recommend_page()
        logger.info(f"导航结果: {nav_result}")

        # 等待页面加载
        await asyncio.sleep(3)

        logger.info(f"✅ 当前URL: {automation.page.url}")

        # 步骤 4: 探索页面结构 - 查找所有可能的职位选择器
        logger.info("\n📍 步骤 4: 探索页面结构")

        # 尝试多种选择器
        selectors_to_try = [
            # 用户提供的选择器
            "#headerWrap > div > div > div.ui-dropmenu.ui-dropmenu-label-arrow.ui-dropmenu-drop-arrow.job-selecter-wrap > div.ui-dropmenu-label",
            # 简化版本
            ".job-selecter-wrap .ui-dropmenu-label",
            ".job-selecter-wrap",
            ".ui-dropmenu-label",
            # 更宽松的查找
            "[class*='job-select']",
            "[class*='dropmenu']",
            "#headerWrap",
        ]

        for selector in selectors_to_try:
            logger.info(f"\n尝试选择器: {selector}")
            elements = await automation.page.query_selector_all(selector)
            if elements:
                logger.info(f"  ✅ 找到 {len(elements)} 个元素")
                for i, elem in enumerate(elements[:3]):  # 只显示前3个
                    html = await elem.evaluate("el => el.outerHTML")
                    logger.info(f"  元素 {i+1}: {html[:200]}...")
            else:
                logger.info(f"  ❌ 未找到")

        # 步骤 5: 获取整个 headerWrap 的 HTML
        logger.info("\n📍 步骤 5: 获取 headerWrap 的完整 HTML")
        header_wrap = await automation.page.query_selector("#headerWrap")
        if header_wrap:
            header_html = await header_wrap.evaluate("el => el.innerHTML")
            logger.info("=" * 80)
            logger.info("headerWrap HTML:")
            logger.info(header_html[:1000])  # 只显示前1000个字符
            logger.info("=" * 80)
        else:
            logger.warning("⚠️ 未找到 #headerWrap")

        # 步骤 6: 查找包含"职位"文本的元素
        logger.info("\n📍 步骤 6: 查找包含职位相关文本的元素")

        # 使用 XPath 查找包含"职位"的元素
        job_related = await automation.page.query_selector_all("text=/职位|岗位|招聘/")
        logger.info(f"找到 {len(job_related)} 个包含职位相关文本的元素")
        for i, elem in enumerate(job_related[:5]):
            text = await elem.text_content()
            html = await elem.evaluate("el => el.outerHTML")
            logger.info(f"  {i+1}. 文本: {text.strip()[:50]}")
            logger.info(f"     HTML: {html[:150]}...")

        # 保持浏览器打开供手动观察
        logger.info("\n⏳ 浏览器将保持打开 60 秒供您手动观察...")
        logger.info("   请在浏览器中手动操作并记录正确的选择器")
        await asyncio.sleep(60)

    except Exception as e:
        logger.error(f"\n❌ 测试失败: {str(e)}", exc_info=True)

    finally:
        logger.info("\n🧹 清理资源...")
        await automation.cleanup()
        logger.info("✅ 测试结束\n")


if __name__ == "__main__":
    asyncio.run(test_job_selector_v2())
