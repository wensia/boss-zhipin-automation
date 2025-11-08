"""
测试二维码登录流程 - 完整版
包含：获取二维码、自动刷新、API 验证登录
"""
import asyncio
from app.services.boss_automation import BossAutomation


async def test_qrcode_login():
    """测试完整的二维码登录流程"""
    print("=" * 70)
    print("Boss 直聘二维码登录流程测试")
    print("=" * 70)

    automation = BossAutomation()

    try:
        # 1. 初始化浏览器
        print("\n📍 步骤 1: 初始化浏览器...")
        success = await automation.initialize(headless=False)
        if not success:
            print("❌ 浏览器初始化失败")
            return
        print("✅ 浏览器初始化成功")

        # 2. 获取二维码
        print("\n📍 步骤 2: 获取登录二维码...")
        qr_result = await automation.get_qrcode()

        if qr_result['success']:
            print(f"✅ 二维码获取成功")
            print(f"   二维码 URL: {qr_result['qrcode'][:100]}...")
        else:
            print(f"❌ 二维码获取失败: {qr_result['message']}")
            return

        # 3. 等待用户扫码
        print("\n📍 步骤 3: 等待用户扫码...")
        print("⚠️  请在浏览器中使用 Boss 直聘 APP 扫描二维码")
        print("⚠️  我将每 3 秒检查一次登录状态和二维码刷新")
        print()

        refresh_count = 0
        max_checks = 60  # 最多检查 60 次（3 分钟）

        for i in range(max_checks):
            await asyncio.sleep(3)

            # 检查登录状态
            print(f"[{i+1}/{max_checks}] 检查登录状态...")
            login_result = await automation.check_login_status()

            if login_result['logged_in']:
                # 登录成功
                print("\n" + "=" * 70)
                print("✅ 登录成功！")
                print("=" * 70)

                user_info = login_result.get('user_info', {})
                if user_info:
                    print(f"👤 用户名: {user_info.get('showName') or user_info.get('name')}")
                    print(f"🏢 公司: {user_info.get('brandName')}")
                    print(f"📧 邮箱: {user_info.get('email')}")
                    print(f"🆔 用户ID: {user_info.get('userId')}")

                print("=" * 70)
                break
            else:
                # 检查是否需要刷新二维码
                if login_result['message'] != '等待扫码':
                    print(f"   ℹ️ {login_result['message']}")

                # 检查并刷新二维码
                refresh_result = await automation.check_and_refresh_qrcode()

                if refresh_result['need_refresh']:
                    refresh_count += 1
                    print(f"   🔄 二维码已过期，自动刷新 (第 {refresh_count} 次)")

                    if refresh_count >= 5:
                        print("\n❌ 二维码刷新次数已达上限（5次），请稍后重试")
                        break

                    if refresh_result['qrcode']:
                        print(f"   ✅ 新二维码已加载")
                    else:
                        print(f"   ❌ 刷新失败: {refresh_result['message']}")

        else:
            print("\n⏱️ 超时：3 分钟内未完成登录")

        # 4. 保持浏览器打开一段时间
        print("\n📍 步骤 4: 浏览器将保持打开 10 秒...")
        await asyncio.sleep(10)

    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        # 5. 清理资源
        print("\n📍 步骤 5: 清理资源...")
        await automation.cleanup()
        print("✅ 清理完成")

    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_qrcode_login())
