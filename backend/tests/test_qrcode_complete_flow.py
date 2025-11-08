"""
完整的二维码获取流程测试
模拟前端的完整操作流程
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


async def test_complete_qrcode_flow():
    """测试完整的二维码获取流程"""
    automation = BossAutomation()

    try:
        logger.info("=" * 80)
        logger.info("🧪 开始测试：完整的二维码获取流程")
        logger.info("=" * 80)

        # 步骤 1: 清除旧的登录状态
        logger.info("\n📍 步骤 1: 清除旧的登录状态文件")
        auth_file = automation.auth_file
        if os.path.exists(auth_file):
            os.remove(auth_file)
            logger.info(f"   ✅ 已删除: {auth_file}")
        else:
            logger.info(f"   ℹ️ 文件不存在: {auth_file}")

        # 步骤 2: 初始化浏览器（非headless，可以看到浏览器）
        logger.info("\n📍 步骤 2: 初始化浏览器（headless=False）")
        init_success = await automation.initialize(headless=False)

        if not init_success:
            logger.error("❌ 浏览器初始化失败")
            return

        logger.info("✅ 浏览器初始化成功")
        await asyncio.sleep(2)

        # 检查浏览器状态
        logger.info("\n📍 步骤 3: 检查浏览器状态")
        logger.info(f"   Browser: {automation.browser is not None}")
        logger.info(f"   Context: {automation.context is not None}")
        logger.info(f"   Page: {automation.page is not None}")

        if automation.page:
            current_url = automation.page.url
            logger.info(f"   当前URL: {current_url}")

        # 步骤 4: 获取二维码
        logger.info("\n📍 步骤 4: 调用 get_qrcode() 方法")
        logger.info("   ⏳ 开始获取二维码...")

        result = await automation.get_qrcode()

        logger.info("\n📊 获取二维码结果:")
        logger.info(f"   success: {result.get('success')}")
        logger.info(f"   message: {result.get('message')}")
        logger.info(f"   already_logged_in: {result.get('already_logged_in', False)}")

        if result.get('qrcode'):
            qrcode = result.get('qrcode')
            logger.info(f"   qrcode: {qrcode[:100]}..." if len(qrcode) > 100 else f"   qrcode: {qrcode}")
        else:
            logger.warning(f"   ⚠️ qrcode 为空")

        # 步骤 5: 再次检查页面状态
        logger.info("\n📍 步骤 5: 再次检查页面状态")
        if automation.page:
            current_url = automation.page.url
            logger.info(f"   当前URL: {current_url}")

            # 检查是否在登录页面
            if 'zhipin.com/web/user/' in current_url:
                logger.info("   ✅ 页面在登录界面")

                # 尝试手动查找二维码元素
                qrcode_selector = '#wrap > div > div.login-entry-page > div.login-register-content > div.scan-app-wrapper > div.qr-code-box > div.qr-img-box > img'
                logger.info(f"\n📍 步骤 6: 手动查找二维码元素")
                logger.info(f"   选择器: {qrcode_selector}")

                try:
                    element = await automation.page.query_selector(qrcode_selector)
                    if element:
                        src = await element.get_attribute('src')
                        logger.info(f"   ✅ 找到二维码元素")
                        logger.info(f"   src: {src[:100] if src and len(src) > 100 else src}")
                    else:
                        logger.warning(f"   ⚠️ 未找到二维码元素")

                        # 列出页面上的所有img元素
                        logger.info("\n📍 查找页面上的所有img元素:")
                        imgs = await automation.page.query_selector_all('img')
                        logger.info(f"   找到 {len(imgs)} 个img元素")

                        for i, img in enumerate(imgs[:5]):  # 只显示前5个
                            src = await img.get_attribute('src')
                            logger.info(f"   [{i+1}] src: {src[:80] if src and len(src) > 80 else src}")

                except Exception as e:
                    logger.error(f"   ❌ 查找二维码元素失败: {str(e)}")
            else:
                logger.warning(f"   ⚠️ 页面不在登录界面")

        # 保持浏览器打开供观察
        logger.info("\n⏳ 浏览器将保持打开 30 秒，请观察...")
        await asyncio.sleep(30)

    except Exception as e:
        logger.error(f"\n❌ 测试失败: {str(e)}", exc_info=True)

    finally:
        logger.info("\n🧹 清理资源...")
        await automation.cleanup()
        logger.info("✅ 测试结束\n")


if __name__ == "__main__":
    asyncio.run(test_complete_qrcode_flow())
