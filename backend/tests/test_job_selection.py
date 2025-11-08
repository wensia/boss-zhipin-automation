"""
测试职位选择功能
验证 select_job_position 和 get_available_jobs 方法
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


async def test_job_selection():
    """测试职位选择功能完整流程"""
    automation = BossAutomation()

    try:
        logger.info("=" * 80)
        logger.info("🧪 测试：职位选择功能")
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
        user_info = login_status.get('user_info', {})
        logger.info(f"   用户: {user_info.get('name', '未知')}")

        # 步骤 3: 导航到推荐页面
        logger.info("\n📍 步骤 3: 导航到推荐页面")
        nav_result = await automation.navigate_to_recommend_page()
        logger.info(f"   导航结果: {nav_result.get('message')}")

        if not nav_result.get('success'):
            logger.error(f"❌ 导航失败: {nav_result.get('message')}")
            return

        logger.info(f"✅ 当前URL: {automation.page.url}")
        await asyncio.sleep(2)

        # 步骤 4: 获取可用职位列表
        logger.info("\n📍 步骤 4: 获取可用职位列表")
        jobs_result = await automation.get_available_jobs()

        if not jobs_result.get('success'):
            logger.error(f"❌ 获取职位列表失败: {jobs_result.get('message')}")
            return

        jobs = jobs_result.get('jobs', [])
        logger.info(f"✅ 成功获取 {len(jobs)} 个职位")

        # 显示所有职位
        logger.info("\n📋 可用职位列表:")
        for i, job in enumerate(jobs, 1):
            logger.info(f"   {i}. {job.get('label')}")
            logger.info(f"      value: {job.get('value')}")

        # 步骤 5: 选择职位（选择第一个职位）
        if len(jobs) > 0:
            logger.info("\n📍 步骤 5: 测试选择职位")

            # 选择第一个职位
            first_job = jobs[0]
            first_job_value = first_job.get('value')
            first_job_label = first_job.get('label')

            logger.info(f"准备选择职位:")
            logger.info(f"   标签: {first_job_label}")
            logger.info(f"   value: {first_job_value}")

            select_result = await automation.select_job_position(job_value=first_job_value)

            if select_result.get('success'):
                logger.info("✅ 职位选择成功")
            else:
                logger.error(f"❌ 职位选择失败: {select_result.get('message')}")

                # 如果失败，显示可用职位
                if 'available_jobs' in select_result:
                    logger.info("可用职位:")
                    for job in select_result['available_jobs']:
                        logger.info(f"   - {job.get('label')} (value: {job.get('value')})")

            await asyncio.sleep(2)

            # 步骤 6: 验证选择结果（可选）
            logger.info("\n📍 步骤 6: 验证选择结果")
            # 可以在这里添加额外的验证逻辑，比如检查页面元素变化等

        else:
            logger.warning("⚠️ 没有可用职位，跳过选择步骤")

        # 保持浏览器打开供观察
        logger.info("\n⏳ 浏览器将保持打开 30 秒供您观察...")
        await asyncio.sleep(30)

    except Exception as e:
        logger.error(f"\n❌ 测试失败: {str(e)}", exc_info=True)

    finally:
        logger.info("\n🧹 清理资源...")
        await automation.cleanup()
        logger.info("✅ 测试结束\n")


async def test_job_selection_with_specific_value():
    """测试选择特定职位（需要手动指定职位 value）"""
    automation = BossAutomation()

    try:
        logger.info("=" * 80)
        logger.info("🧪 测试：选择特定职位")
        logger.info("=" * 80)

        # 初始化
        init_success = await automation.initialize(headless=False)
        if not init_success:
            logger.error("❌ 浏览器初始化失败")
            return

        # 检查登录
        login_status = await automation.check_login_status()
        if not login_status.get('logged_in'):
            logger.error("❌ 未登录，测试终止")
            return

        # 导航到推荐页面
        await automation.navigate_to_recommend_page()
        await asyncio.sleep(2)

        # TODO: 替换为实际的职位 value
        # 你可以从 get_available_jobs() 的结果中获取 value
        target_job_value = "bc9d6c8eac63563603x93dS0GVtV"  # 示例 value

        logger.info(f"\n📍 准备选择职位: {target_job_value}")

        select_result = await automation.select_job_position(job_value=target_job_value)

        if select_result.get('success'):
            logger.info("✅ 职位选择成功")
        else:
            logger.error(f"❌ 职位选择失败: {select_result.get('message')}")

        await asyncio.sleep(10)

    except Exception as e:
        logger.error(f"\n❌ 测试失败: {str(e)}", exc_info=True)

    finally:
        await automation.cleanup()
        logger.info("✅ 测试结束\n")


if __name__ == "__main__":
    # 运行完整测试
    asyncio.run(test_job_selection())

    # 或运行特定职位选择测试（取消注释下面的行）
    # asyncio.run(test_job_selection_with_specific_value())
