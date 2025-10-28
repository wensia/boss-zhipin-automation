"""
测试登录流程脚本
"""
import asyncio
from app.services.boss_automation import BossAutomation


async def test_login():
    """测试登录流程"""
    print("=" * 60)
    print("Boss 直聘登录测试")
    print("=" * 60)

    automation = BossAutomation()

    try:
        # 1. 初始化浏览器
        print("\n📍 步骤 1: 初始化浏览器...")
        success = await automation.initialize(headless=False)
        if not success:
            print("❌ 浏览器初始化失败")
            return
        print("✅ 浏览器初始化成功")

        # 2. 检查并登录
        print("\n📍 步骤 2: 检查登录状态...")
        is_logged_in = await automation.check_and_login()

        if is_logged_in:
            print("✅ 登录成功！")
            print(f"   登录状态已保存到: {automation.auth_file}")
        else:
            print("❌ 登录失败或被取消")

        # 3. 保持浏览器打开，等待用户查看
        print("\n📍 步骤 3: 浏览器将保持打开 30 秒，您可以查看页面状态...")
        await asyncio.sleep(30)

    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        # 4. 清理资源
        print("\n📍 步骤 4: 清理资源...")
        await automation.cleanup()
        print("✅ 清理完成")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_login())
