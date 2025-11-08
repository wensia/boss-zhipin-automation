"""
测试登录后自动导航到推荐牛人页面
"""
import asyncio
from app.services.boss_automation import BossAutomation


async def test_recommend_navigate():
    """测试自动导航到推荐页面"""
    print("=" * 70)
    print("测试登录后自动导航到推荐牛人页面")
    print("=" * 70)

    automation = BossAutomation()

    try:
        # 1. 初始化浏览器（会加载之前保存的 session）
        print("\n📍 步骤 1: 初始化浏览器...")
        success = await automation.initialize(headless=False)
        if not success:
            print("❌ 浏览器初始化失败")
            return
        print("✅ 浏览器初始化成功")

        # 2. 尝试获取二维码（如果已登录会自动导航）
        print("\n📍 步骤 2: 调用 get_qrcode()...")
        print("   预期：如果已登录，会自动导航到推荐页面")

        result = await automation.get_qrcode()

        print("\n" + "=" * 70)
        print("返回结果:")
        print("=" * 70)
        print(f"success: {result.get('success')}")
        print(f"already_logged_in: {result.get('already_logged_in')}")
        print(f"message: {result.get('message')}")

        # 检查导航结果
        navigate_result = result.get('navigate_result')
        if navigate_result:
            print("\n导航结果:")
            print(f"  ✅ 成功: {navigate_result.get('success')}")
            print(f"  📍 方法: {navigate_result.get('method')}")
            print(f"  🔗 URL: {navigate_result.get('url')}")
            print(f"  💬 消息: {navigate_result.get('message')}")

        if result.get('already_logged_in'):
            print("\n✅ 已登录状态检测成功！")
            print("\n用户信息:")
            user_info = result.get('user_info', {})
            print(f"  👤 用户名: {user_info.get('showName')}")
            print(f"  🏢 公司: {user_info.get('brandName')}")
            print(f"  📧 邮箱: {user_info.get('email')}")
        elif result.get('qrcode'):
            print("\n⚠️ 需要扫码登录")
            print(f"   二维码 URL: {result.get('qrcode')[:80]}...")

            # 等待扫码并轮询登录状态
            print("\n⏳ 等待扫码登录...")
            for i in range(60):  # 最多等待3分钟
                await asyncio.sleep(3)
                print(f"[{i+1}/60] 检查登录状态...")

                login_result = await automation.check_login_status()

                if login_result['logged_in']:
                    print("\n" + "=" * 70)
                    print("✅ 登录成功！")
                    print("=" * 70)

                    # 检查导航结果
                    nav_result = login_result.get('navigate_result')
                    if nav_result:
                        print("\n导航结果:")
                        print(f"  ✅ 成功: {nav_result.get('success')}")
                        print(f"  📍 方法: {nav_result.get('method')}")
                        print(f"  🔗 URL: {nav_result.get('url')}")
                        print(f"  💬 消息: {nav_result.get('message')}")

                    user_info = login_result.get('user_info', {})
                    print(f"\n👤 用户名: {user_info.get('showName')}")
                    print(f"🏢 公司: {user_info.get('brandName')}")
                    break

        print("=" * 70)

        # 3. 保持浏览器打开一段时间以便查看
        print("\n📍 步骤 3: 浏览器将保持打开 15 秒...")
        await asyncio.sleep(15)

    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        # 4. 清理资源
        print("\n📍 步骤 4: 清理资源...")
        await automation.cleanup()
        print("✅ 清理完成")

    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_recommend_navigate())
