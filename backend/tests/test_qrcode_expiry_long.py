"""
长时间测试：等待二维码过期并测试自动刷新
保持浏览器运行，观察二维码过期和刷新的完整流程
"""
import asyncio
import logging
from datetime import datetime
from app.services.boss_automation import BossAutomation

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_qrcode_expiry_long_run():
    """长时间测试：等待二维码过期并测试刷新"""
    automation = BossAutomation()

    try:
        logger.info("=" * 80)
        logger.info("🧪 长时间测试：等待二维码过期并测试自动刷新")
        logger.info("=" * 80)
        logger.info("本测试将：")
        logger.info("  1. 初始化浏览器并获取二维码")
        logger.info("  2. 等待约 3 分钟让二维码过期")
        logger.info("  3. 每30秒检测一次过期状态")
        logger.info("  4. 检测到过期后自动刷新")
        logger.info("  5. 保持浏览器运行供观察")
        logger.info("")

        # 步骤 1: 初始化浏览器
        logger.info("📍 步骤 1: 初始化浏览器（headless=False，可见）")
        start_time = datetime.now()

        init_success = await automation.initialize(headless=False)
        if not init_success:
            logger.error("❌ 浏览器初始化失败")
            return

        logger.info("✅ 浏览器初始化成功")
        logger.info(f"   启动时间: {start_time.strftime('%H:%M:%S')}")
        await asyncio.sleep(2)

        # 步骤 2: 获取初始二维码
        logger.info("\n📍 步骤 2: 获取初始二维码")
        result1 = await automation.get_qrcode()

        if not result1.get('success'):
            logger.error(f"❌ 获取二维码失败: {result1.get('message')}")
            return

        initial_qrcode = result1.get('qrcode', '')
        logger.info(f"✅ 成功获取二维码")
        logger.info(f"   URL前缀: {initial_qrcode[:80]}...")
        logger.info(f"   获取时间: {datetime.now().strftime('%H:%M:%S')}")

        # 步骤 3: 定期检测二维码状态
        logger.info("\n📍 步骤 3: 开始监控二维码状态")
        logger.info("⏳ Boss直聘二维码有效期约 2-3 分钟")
        logger.info("⏳ 将每30秒检测一次，持续5分钟...")
        logger.info("")

        check_count = 0
        expired_detected = False
        refresh_count = 0

        # 总共检测 10 次，每次间隔 30 秒 = 5 分钟
        for i in range(10):
            check_count += 1
            elapsed = (datetime.now() - start_time).total_seconds()
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)

            logger.info(f"━━━ 第 {check_count} 次检测 (已运行 {minutes}分{seconds}秒) ━━━")

            # 检查是否需要刷新
            refresh_result = await automation.check_and_refresh_qrcode()

            if refresh_result.get('need_refresh'):
                if not expired_detected:
                    logger.info("🎯 首次检测到二维码过期！")
                    expired_detected = True

                refresh_count += 1
                logger.info(f"🔄 第 {refresh_count} 次自动刷新")

                if refresh_result.get('qrcode'):
                    new_qrcode = refresh_result.get('qrcode')
                    logger.info(f"✅ 刷新成功")
                    logger.info(f"   新二维码: {new_qrcode[:80]}...")
                    logger.info(f"   是否变化: {'是' if new_qrcode != initial_qrcode else '否'}")
                else:
                    logger.warning(f"⚠️ 刷新失败: {refresh_result.get('message')}")
            else:
                status = "有效" if not expired_detected else "刷新后有效"
                logger.info(f"✓ 二维码状态: {status}")
                logger.info(f"  消息: {refresh_result.get('message')}")

            # 手动检查页面上的刷新按钮
            try:
                refresh_button_selector = '#wrap > div > div.login-entry-page > div.login-register-content > div.scan-app-wrapper > div.qr-code-box > div.qr-img-box > div > button'
                refresh_button = await automation.page.query_selector(refresh_button_selector)

                if refresh_button:
                    button_text = await refresh_button.text_content()
                    logger.info(f"  🔘 页面上有刷新按钮: '{button_text}'")
                else:
                    logger.info(f"  ✓ 页面上没有刷新按钮（二维码有效）")
            except Exception as e:
                logger.warning(f"  ⚠️ 检查刷新按钮失败: {str(e)}")

            logger.info("")

            # 等待 30 秒再检测
            if i < 9:  # 最后一次不需要等待
                logger.info("⏳ 等待 30 秒后继续检测...")
                await asyncio.sleep(30)

        # 步骤 4: 总结
        logger.info("\n" + "=" * 80)
        logger.info("📊 测试总结")
        logger.info("=" * 80)
        total_elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"总运行时间: {int(total_elapsed // 60)} 分 {int(total_elapsed % 60)} 秒")
        logger.info(f"检测次数: {check_count}")
        logger.info(f"过期检测: {'✅ 是' if expired_detected else '❌ 否'}")
        logger.info(f"刷新次数: {refresh_count}")
        logger.info("")

        # 步骤 5: 最后再获取一次二维码测试
        logger.info("📍 步骤 5: 最后测试 - 再次调用 get_qrcode()")
        final_result = await automation.get_qrcode()

        if final_result.get('success'):
            final_qrcode = final_result.get('qrcode', '')
            logger.info(f"✅ 获取成功")
            logger.info(f"   消息: {final_result.get('message')}")
            logger.info(f"   与初始二维码相比: {'已更新' if final_qrcode != initial_qrcode else '相同'}")
        else:
            logger.error(f"❌ 获取失败: {final_result.get('message')}")

        # 保持浏览器打开供观察
        logger.info("\n⏳ 测试完成！浏览器将保持打开 60 秒供您观察...")
        logger.info("   您可以手动扫码测试登录流程")
        await asyncio.sleep(60)

    except KeyboardInterrupt:
        logger.info("\n\n⚠️ 用户中断测试")
    except Exception as e:
        logger.error(f"\n❌ 测试失败: {str(e)}", exc_info=True)

    finally:
        logger.info("\n🧹 清理资源...")
        await automation.cleanup()
        logger.info("✅ 测试结束\n")


if __name__ == "__main__":
    logger.info("提示：本测试需要约 5-6 分钟")
    logger.info("请保持终端窗口打开，观察测试过程")
    logger.info("按 Ctrl+C 可随时中断测试")
    logger.info("")

    asyncio.run(test_qrcode_expiry_long_run())
