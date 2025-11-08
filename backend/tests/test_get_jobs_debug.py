"""
调试测试：获取可用职位列表
详细输出每一步的信息，帮助定位问题
"""
import asyncio
import logging
from app.services.boss_automation import BossAutomation

# 配置日志 - 显示更详细的信息
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_get_jobs_with_debug():
    """测试获取职位列表（带详细调试信息）"""
    automation = BossAutomation()

    try:
        logger.info("=" * 80)
        logger.info("🧪 测试：获取可用职位列表（调试模式）")
        logger.info("=" * 80)

        # 步骤 1: 初始化浏览器（显示浏览器窗口以便观察）
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
            logger.info("💡 提示：请先运行登录流程")
            return

        logger.info("✅ 已登录")
        user_info = login_status.get('user_info', {})
        logger.info(f"   用户: {user_info.get('name', '未知')}")

        # 步骤 3: 导航到推荐页面
        logger.info("\n📍 步骤 3: 导航到推荐页面")
        nav_result = await automation.navigate_to_recommend_page()
        logger.info(f"   导航结果: {nav_result.get('message')}")

        if not nav_result.get('success'):
            logger.error(f"❌ 导航失败: {nav_result.get('message')}")
            return

        current_url = automation.page.url
        logger.info(f"✅ 当前URL: {current_url}")
        await asyncio.sleep(3)

        # 步骤 4: 获取职位列表（核心测试）
        logger.info("\n" + "=" * 80)
        logger.info("📍 步骤 4: 调用 get_available_jobs()")
        logger.info("=" * 80)

        result = await automation.get_available_jobs()

        # 打印结果
        logger.info("\n" + "=" * 80)
        logger.info("📊 测试结果:")
        logger.info("=" * 80)
        logger.info(f"成功: {result.get('success')}")
        logger.info(f"消息: {result.get('message')}")
        logger.info(f"职位数量: {result.get('total', 0)}")

        if result.get('success'):
            jobs = result.get('jobs', [])
            logger.info(f"\n✅ 成功获取 {len(jobs)} 个职位:")
            for idx, job in enumerate(jobs, 1):
                logger.info(f"\n  职位 {idx}:")
                logger.info(f"    value: {job.get('value')}")
                logger.info(f"    label: {job.get('label')}")
        else:
            logger.error(f"\n❌ 获取失败: {result.get('message')}")

        # 步骤 5: 手动检查页面
        logger.info("\n" + "=" * 80)
        logger.info("📍 步骤 5: 手动检查页面元素")
        logger.info("=" * 80)

        # 检查 headerWrap 是否存在
        header_exists = await automation.page.evaluate("""
            () => {
                const header = document.querySelector('#headerWrap');
                return !!header;
            }
        """)
        logger.info(f"#headerWrap 存在: {header_exists}")

        # 检查职位选择器是否存在
        selector_exists = await automation.page.evaluate("""
            () => {
                const selector = document.querySelector('.job-selecter-wrap');
                return !!selector;
            }
        """)
        logger.info(f".job-selecter-wrap 存在: {selector_exists}")

        # 如果选择器存在，打印其HTML
        if selector_exists:
            selector_html = await automation.page.evaluate("""
                () => {
                    const selector = document.querySelector('.job-selecter-wrap');
                    return selector ? selector.outerHTML : '';
                }
            """)
            logger.info(f"\n职位选择器HTML (前500字符):")
            logger.info(selector_html[:500])

        # 保持浏览器打开供手动检查
        logger.info("\n⏳ 浏览器将保持打开 60 秒供您手动检查...")
        logger.info("   请手动点击职位选择器，查看下拉菜单是否正常显示")
        await asyncio.sleep(60)

    except Exception as e:
        logger.error(f"\n❌ 测试失败: {str(e)}", exc_info=True)

    finally:
        logger.info("\n🧹 清理资源...")
        await automation.cleanup()
        logger.info("✅ 测试结束\n")


if __name__ == "__main__":
    asyncio.run(test_get_jobs_with_debug())
