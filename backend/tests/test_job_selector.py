"""
测试职位选择器功能
在推荐牛人页面选择指定的招聘职位
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


async def test_job_selector():
    """测试职位选择器"""
    automation = BossAutomation()

    try:
        logger.info("=" * 80)
        logger.info("🧪 测试：推荐牛人页面职位选择器")
        logger.info("=" * 80)

        # 步骤 1: 初始化浏览器
        logger.info("\n📍 步骤 1: 初始化浏览器（headless=False，可见）")
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
            logger.warning("⚠️ 未登录，需要先登录")
            logger.info("请手动登录后继续...")
            # 等待用户登录
            await asyncio.sleep(30)

            # 再次检查
            login_status = await automation.check_login_status()
            if not login_status.get('logged_in'):
                logger.error("❌ 仍未登录，测试终止")
                return

        logger.info("✅ 已登录")
        logger.info(f"   用户: {login_status.get('user_info', {}).get('name', '未知')}")

        # 步骤 3: 导航到推荐牛人页面
        logger.info("\n📍 步骤 3: 导航到推荐牛人页面")
        recommend_url = "https://www.zhipin.com/web/geek/recommend"
        await automation.page.goto(recommend_url, wait_until='domcontentloaded', timeout=30000)
        logger.info(f"✅ 已导航到: {recommend_url}")

        # 等待页面加载
        await asyncio.sleep(3)

        # 步骤 4: 检查职位选择器
        logger.info("\n📍 步骤 4: 查找职位选择器")

        # 职位选择器触发器
        selector_trigger = "#headerWrap > div > div > div.ui-dropmenu.ui-dropmenu-label-arrow.ui-dropmenu-drop-arrow.job-selecter-wrap > div.ui-dropmenu-label"

        # 尝试更宽松的选择器
        trigger_element = await automation.page.query_selector(selector_trigger)

        if not trigger_element:
            logger.warning("⚠️ 使用精确选择器未找到，尝试宽松选择器...")
            # 尝试更宽松的选择器
            trigger_element = await automation.page.query_selector(".job-selecter-wrap .ui-dropmenu-label")

        if not trigger_element:
            logger.error("❌ 未找到职位选择器")
            # 打印页面HTML以供调试
            html = await automation.page.content()
            logger.debug(f"页面HTML: {html[:500]}...")
            return

        logger.info("✅ 找到职位选择器")

        # 步骤 5: 点击触发器打开下拉菜单
        logger.info("\n📍 步骤 5: 点击职位选择器打开下拉菜单")
        await trigger_element.click()
        logger.info("✅ 已点击触发器")

        # 等待下拉菜单出现
        await asyncio.sleep(1)

        # 步骤 6: 获取职位列表
        logger.info("\n📍 步骤 6: 获取职位列表")

        # 下拉列表选择器
        list_selector = "#headerWrap > div > div > div.ui-dropmenu.ui-dropmenu-visible.ui-dropmenu-label-arrow.ui-dropmenu-drop-arrow.job-selecter-wrap.expanding > div.ui-dropmenu-list > ul"

        # 尝试更宽松的选择器
        list_element = await automation.page.query_selector(list_selector)

        if not list_element:
            logger.warning("⚠️ 使用精确选择器未找到列表，尝试宽松选择器...")
            list_element = await automation.page.query_selector(".job-selecter-wrap.expanding .ui-dropmenu-list ul")

        if not list_element:
            logger.error("❌ 未找到职位列表")
            return

        logger.info("✅ 找到职位列表")

        # 步骤 7: 获取所有职位选项
        logger.info("\n📍 步骤 7: 获取所有职位选项")

        job_items = await list_element.query_selector_all("li.job-item")
        logger.info(f"✅ 找到 {len(job_items)} 个职位选项")

        # 遍历并显示所有职位
        logger.info("\n职位列表:")
        for i, item in enumerate(job_items, 1):
            value = await item.get_attribute("value")
            label_element = await item.query_selector(".label")
            label_text = await label_element.text_content() if label_element else "无标签"
            logger.info(f"  {i}. value={value}")
            logger.info(f"     标签: {label_text.strip()}")

        # 步骤 8: 测试选择第一个职位
        if len(job_items) > 0:
            logger.info("\n📍 步骤 8: 测试选择第一个职位")
            first_item = job_items[0]
            first_value = await first_item.get_attribute("value")
            logger.info(f"准备选择职位: value={first_value}")

            await first_item.click()
            logger.info("✅ 已点击职位选项")

            await asyncio.sleep(2)

            # 验证选择是否成功
            logger.info("📍 验证选择结果")
            # 检查下拉菜单是否关闭
            menu_closed = await automation.page.query_selector(".job-selecter-wrap:not(.expanding)")
            if menu_closed:
                logger.info("✅ 下拉菜单已关闭，选择成功")
            else:
                logger.warning("⚠️ 下拉菜单仍然打开")

        # 保持浏览器打开供观察
        logger.info("\n⏳ 浏览器将保持打开 30 秒供您观察...")
        await asyncio.sleep(30)

    except Exception as e:
        logger.error(f"\n❌ 测试失败: {str(e)}", exc_info=True)

    finally:
        logger.info("\n🧹 清理资源...")
        await automation.cleanup()
        logger.info("✅ 测试结束\n")


if __name__ == "__main__":
    asyncio.run(test_job_selector())
