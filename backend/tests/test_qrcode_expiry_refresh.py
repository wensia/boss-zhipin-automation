"""
测试二维码过期后的自动刷新流程
模拟等待二维码过期，然后测试自动刷新
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


async def test_qrcode_expiry_and_refresh():
    """测试二维码过期和自动刷新"""
    automation = BossAutomation()

    try:
        logger.info("=" * 80)
        logger.info("🧪 测试：二维码过期后自动刷新")
        logger.info("=" * 80)

        # 步骤 1: 初始化浏览器
        logger.info("\n📍 步骤 1: 初始化浏览器")
        init_success = await automation.initialize(headless=False)
        if not init_success:
            logger.error("❌ 浏览器初始化失败")
            return

        logger.info("✅ 浏览器初始化成功")
        await asyncio.sleep(2)

        # 步骤 2: 第一次获取二维码
        logger.info("\n📍 步骤 2: 第一次获取二维码")
        result1 = await automation.get_qrcode()
        logger.info(f"第一次获取结果:")
        logger.info(f"  success: {result1.get('success')}")
        logger.info(f"  message: {result1.get('message')}")
        if result1.get('qrcode'):
            logger.info(f"  qrcode: {result1.get('qrcode')[:80]}...")

        # 步骤 3: 等待二维码过期 (约 3 分钟)
        logger.info("\n📍 步骤 3: 等待二维码过期...")
        logger.info("⏳ Boss直聘的二维码通常 2-3 分钟后过期")
        logger.info("⏳ 等待 180 秒 (3分钟)...")

        for i in range(180, 0, -30):
            logger.info(f"   还剩 {i} 秒...")
            await asyncio.sleep(30)

        logger.info("✅ 等待完成，二维码应该已经过期")

        # 步骤 4: 检查二维码状态（应该检测到过期）
        logger.info("\n📍 步骤 4: 检查二维码是否过期")
        refresh_result = await automation.check_and_refresh_qrcode()
        logger.info(f"检查结果:")
        logger.info(f"  need_refresh: {refresh_result.get('need_refresh')}")
        logger.info(f"  message: {refresh_result.get('message')}")
        if refresh_result.get('qrcode'):
            logger.info(f"  qrcode: {refresh_result.get('qrcode')[:80]}...")

        # 步骤 5: 再次调用 get_qrcode（应该自动刷新）
        logger.info("\n📍 步骤 5: 再次获取二维码（应该自动刷新）")
        result2 = await automation.get_qrcode()
        logger.info(f"第二次获取结果:")
        logger.info(f"  success: {result2.get('success')}")
        logger.info(f"  message: {result2.get('message')}")
        if result2.get('qrcode'):
            logger.info(f"  qrcode: {result2.get('qrcode')[:80]}...")

        # 比较两次的二维码
        if result1.get('qrcode') and result2.get('qrcode'):
            if result1.get('qrcode') != result2.get('qrcode'):
                logger.info("\n✅ 成功：二维码已更新（两次不同）")
            else:
                logger.warning("\n⚠️ 警告：两次二维码相同，可能未正确刷新")

        # 步骤 6: 手动查找刷新按钮
        logger.info("\n📍 步骤 6: 手动检查页面上的刷新按钮")
        refresh_button_selector = '#wrap > div > div.login-entry-page > div.login-register-content > div.scan-app-wrapper > div.qr-code-box > div.qr-img-box > div > button'

        try:
            refresh_button = await automation.page.query_selector(refresh_button_selector)
            if refresh_button:
                logger.info("  ✅ 找到刷新按钮（二维码已过期）")
                button_text = await refresh_button.text_content()
                logger.info(f"  按钮文本: {button_text}")
            else:
                logger.info("  ℹ️ 未找到刷新按钮（二维码未过期或已刷新）")
        except Exception as e:
            logger.error(f"  ❌ 检查刷新按钮失败: {str(e)}")

        # 保持浏览器打开
        logger.info("\n⏳ 浏览器将保持打开 30 秒，请观察...")
        await asyncio.sleep(30)

    except Exception as e:
        logger.error(f"\n❌ 测试失败: {str(e)}", exc_info=True)

    finally:
        logger.info("\n🧹 清理资源...")
        await automation.cleanup()
        logger.info("✅ 测试结束\n")


async def test_quick_refresh_check():
    """快速测试刷新检测功能（不等待过期）"""
    automation = BossAutomation()

    try:
        logger.info("=" * 80)
        logger.info("🧪 快速测试：刷新检测功能")
        logger.info("=" * 80)

        # 初始化
        logger.info("\n📍 初始化浏览器")
        await automation.initialize(headless=False)
        await asyncio.sleep(2)

        # 获取二维码
        logger.info("\n📍 获取二维码")
        result = await automation.get_qrcode()
        logger.info(f"结果: {result.get('success')} - {result.get('message')}")

        # 多次检查刷新状态
        logger.info("\n📍 连续检查刷新状态 (5次，每次间隔2秒)")
        for i in range(5):
            logger.info(f"\n第 {i+1} 次检查:")
            refresh_result = await automation.check_and_refresh_qrcode()
            logger.info(f"  need_refresh: {refresh_result.get('need_refresh')}")
            logger.info(f"  message: {refresh_result.get('message')}")

            if refresh_result.get('need_refresh'):
                logger.info("  🔄 检测到需要刷新")
                if refresh_result.get('qrcode'):
                    logger.info(f"  ✅ 已自动刷新")

            await asyncio.sleep(2)

        # 保持浏览器打开
        logger.info("\n⏳ 浏览器将保持打开 20 秒...")
        await asyncio.sleep(20)

    except Exception as e:
        logger.error(f"\n❌ 测试失败: {str(e)}", exc_info=True)

    finally:
        logger.info("\n🧹 清理资源...")
        await automation.cleanup()
        logger.info("✅ 测试结束\n")


async def main():
    """主测试函数"""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'quick':
        # 快速测试模式
        await test_quick_refresh_check()
    else:
        # 完整测试模式（等待过期）
        logger.info("提示：完整测试将等待 3 分钟让二维码过期")
        logger.info("如果想快速测试，运行: python test_qrcode_expiry_refresh.py quick")
        logger.info("")
        await test_qrcode_expiry_and_refresh()


if __name__ == "__main__":
    asyncio.run(main())
