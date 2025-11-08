"""
测试更新后的 get_available_jobs() 方法
"""
import asyncio
import logging
from pathlib import Path
from app.services.boss_automation import BossAutomation

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)


async def test_final_get_jobs():
    """测试最终版本的 get_available_jobs"""
    automation = BossAutomation()

    try:
        logger.info("=" * 80)
        logger.info("🧪 测试 get_available_jobs() 方法")
        logger.info("=" * 80)

        # 初始化
        await automation.initialize(headless=False)
        await asyncio.sleep(2)

        # 登录检查
        login_status = await automation.check_login_status()
        if not login_status.get('logged_in'):
            logger.error("❌ 未登录")
            return

        logger.info("✅ 已登录")

        # 导航到推荐页面
        logger.info("\n📍 导航到推荐页面...")
        await automation.navigate_to_recommend_page()
        await asyncio.sleep(3)

        # 调用 get_available_jobs
        logger.info("\n" + "=" * 80)
        logger.info("📞 调用 get_available_jobs()")
        logger.info("=" * 80)

        result = await automation.get_available_jobs()

        # 打印结果
        logger.info("\n" + "=" * 80)
        logger.info("📊 结果:")
        logger.info("=" * 80)
        logger.info(f"成功: {result.get('success')}")
        logger.info(f"消息: {result.get('message')}")
        logger.info(f"职位总数: {result.get('total', 0)}")

        if result.get('success'):
            jobs = result.get('jobs', [])
            logger.info(f"\n✅ 成功获取 {len(jobs)} 个职位:")

            for idx, job in enumerate(jobs, 1):
                logger.info(f"\n职位 {idx}:")
                logger.info(f"  value: {job.get('value')}")
                logger.info(f"  label: {job.get('label')}")
        else:
            logger.error(f"\n❌ 获取失败: {result.get('message')}")

        # 截图
        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "final_test_result.png"))
        logger.info("\n📸 已保存截图")

        # 保持浏览器打开
        logger.info("\n⏳ 浏览器将保持打开 60 秒...")
        await asyncio.sleep(60)

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}", exc_info=True)

    finally:
        await automation.cleanup()


if __name__ == "__main__":
    asyncio.run(test_final_get_jobs())
