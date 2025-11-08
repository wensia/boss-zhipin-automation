"""
测试登录失效状态下的二维码获取
模拟session过期但is_logged_in=True的情况
"""
import asyncio
import logging
import os
from app.services.boss_automation import BossAutomation

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_expired_session_qrcode():
    """测试session过期时获取二维码"""
    automation = BossAutomation()

    try:
        logger.info("=" * 80)
        logger.info("🧪 测试场景：session过期时获取二维码")
        logger.info("=" * 80)

        # 1. 初始化浏览器
        logger.info("\n📍 步骤 1: 初始化浏览器")
        await automation.init_browser(headless=False)
        await asyncio.sleep(2)

        # 2. 模拟已登录状态（但session实际已过期）
        logger.info("\n📍 步骤 2: 模拟过期的登录状态")
        logger.info("   设置 is_logged_in = True（模拟上次登录）")
        automation.is_logged_in = True

        # 检查是否有auth文件
        if os.path.exists(automation.auth_file):
            logger.info(f"   发现登录状态文件: {automation.auth_file}")
            # 可以选择删除它来模拟session过期
            # os.remove(automation.auth_file)
        else:
            logger.info("   没有登录状态文件")

        # 3. 尝试获取二维码
        logger.info("\n📍 步骤 3: 尝试获取二维码")
        logger.info("   预期：如果session过期，应该能成功获取二维码")

        result = await automation.get_qrcode()

        logger.info(f"\n📊 获取二维码结果:")
        logger.info(f"   success: {result.get('success')}")
        logger.info(f"   message: {result.get('message')}")
        logger.info(f"   已登录: {result.get('already_logged_in', False)}")

        if result.get('qrcode'):
            logger.info(f"   二维码: {result.get('qrcode')[:100]}...")
        else:
            logger.info(f"   二维码: (空)")

        # 4. 分析结果
        logger.info("\n📊 问题分析:")
        if not result.get('success') and '已登录' in result.get('message', ''):
            logger.error("❌ 问题发现：系统错误地认为已登录，无法获取二维码")
            logger.error("   这就是用户报告的问题！")
            logger.error("   原因：is_logged_in 标志为 True，但实际session可能已过期")
        elif result.get('success') and result.get('qrcode'):
            logger.info("✅ 成功获取二维码，问题已修复或不存在")
        elif result.get('already_logged_in'):
            logger.info("✅ 检测到已登录且验证通过")
        else:
            logger.warning(f"⚠️ 其他情况: {result.get('message')}")

        # 5. 测试check_login_status
        logger.info("\n📍 步骤 4: 测试登录状态检查")
        login_status = await automation.check_login_status()
        logger.info(f"   logged_in: {login_status.get('logged_in')}")
        logger.info(f"   message: {login_status.get('message')}")

        # 保持浏览器打开
        logger.info("\n⏳ 浏览器将保持打开 15 秒，请观察...")
        await asyncio.sleep(15)

    except Exception as e:
        logger.error(f"❌ 测试失败: {str(e)}", exc_info=True)

    finally:
        logger.info("\n🧹 清理资源...")
        await automation.cleanup()
        logger.info("✅ 测试结束")


async def test_force_logout_then_qrcode():
    """测试：强制退出登录后获取二维码"""
    automation = BossAutomation()

    try:
        logger.info("\n" + "=" * 80)
        logger.info("🧪 测试场景：强制退出登录后获取二维码")
        logger.info("=" * 80)

        # 1. 初始化浏览器
        logger.info("\n📍 步骤 1: 初始化浏览器")
        await automation.init_browser(headless=False)
        await asyncio.sleep(2)

        # 2. 删除登录状态文件
        logger.info("\n📍 步骤 2: 删除登录状态文件（模拟强制退出）")
        if os.path.exists(automation.auth_file):
            os.remove(automation.auth_file)
            logger.info(f"   已删除: {automation.auth_file}")

        # 清除浏览器cookies
        logger.info("   清除浏览器cookies...")
        await automation.context.clear_cookies()

        automation.is_logged_in = False
        logger.info("   设置 is_logged_in = False")

        # 3. 获取二维码
        logger.info("\n📍 步骤 3: 获取二维码")
        result = await automation.get_qrcode()

        logger.info(f"\n📊 获取二维码结果:")
        logger.info(f"   success: {result.get('success')}")
        logger.info(f"   message: {result.get('message')}")

        if result.get('success') and result.get('qrcode'):
            logger.info("✅ 成功获取二维码")
            logger.info(f"   二维码URL: {result.get('qrcode')[:100]}...")
        else:
            logger.error(f"❌ 获取二维码失败: {result.get('message')}")

        # 保持浏览器打开
        logger.info("\n⏳ 浏览器将保持打开 15 秒，请观察...")
        await asyncio.sleep(15)

    except Exception as e:
        logger.error(f"❌ 测试失败: {str(e)}", exc_info=True)

    finally:
        logger.info("\n🧹 清理资源...")
        await automation.cleanup()
        logger.info("✅ 测试结束")


async def main():
    """主测试函数"""
    logger.info("🧪 开始二维码获取测试")
    logger.info("=" * 80)

    # 测试 1: session过期但is_logged_in=True
    await test_expired_session_qrcode()

    await asyncio.sleep(3)

    # 测试 2: 强制退出后获取二维码
    await test_force_logout_then_qrcode()

    logger.info("\n" + "=" * 80)
    logger.info("🎉 所有测试完成！")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
