"""
测试已登录场景
如果之前已经登录过，session 还在，点击登录后会直接跳转到聊天页面
"""
import asyncio
from app.services.boss_automation import BossAutomation


async def test_already_logged_in():
    """测试已登录场景"""
    print("=" * 70)
    print("测试已登录场景 - 直接验证用户信息")
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
        print("   (已加载之前保存的登录状态)")

        # 2. 尝试获取二维码（实际会检测到已登录）
        print("\n📍 步骤 2: 调用 get_qrcode() 方法...")
        print("   预期：检测到已登录，直接返回用户信息")

        result = await automation.get_qrcode()

        print("\n" + "=" * 70)
        print("返回结果:")
        print("=" * 70)
        print(f"success: {result.get('success')}")
        print(f"already_logged_in: {result.get('already_logged_in')}")
        print(f"message: {result.get('message')}")

        if result.get('already_logged_in'):
            print("\n✅ 成功检测到已登录状态！")
            print("\n用户信息:")
            user_info = result.get('user_info', {})
            print(f"  👤 用户名: {user_info.get('showName') or user_info.get('name')}")
            print(f"  🏢 公司: {user_info.get('brandName')}")
            print(f"  📧 邮箱: {user_info.get('email')}")
            print(f"  🆔 用户ID: {user_info.get('userId')}")
            print(f"  📸 头像: {user_info.get('avatar')[:50] if user_info.get('avatar') else 'N/A'}...")
        elif result.get('qrcode'):
            print("\n⚠️ 返回了二维码（可能 session 已过期）")
            print(f"   二维码 URL: {result.get('qrcode')[:80]}...")
        else:
            print(f"\n❌ 返回异常: {result.get('message')}")

        print("=" * 70)

        # 3. 保持浏览器打开一段时间
        print("\n📍 步骤 3: 浏览器将保持打开 10 秒...")
        await asyncio.sleep(10)

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
    asyncio.run(test_already_logged_in())
