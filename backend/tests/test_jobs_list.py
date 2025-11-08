"""
测试获取已沟通职位列表功能
"""
import asyncio
from app.services.boss_automation import BossAutomation


async def test_jobs_list():
    """测试获取职位列表"""
    print("=" * 70)
    print("测试获取已沟通职位列表功能")
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

        # 2. 检查登录状态
        print("\n📍 步骤 2: 检查登录状态...")
        login_result = await automation.check_login_status()

        if not login_result.get('logged_in'):
            print("⚠️ 未登录，需要先登录")
            print("   请先运行登录测试脚本: python test_recommend_navigate.py")
            return

        print("✅ 已登录")
        user_info = login_result.get('user_info', {})
        print(f"   👤 用户名: {user_info.get('showName')}")
        print(f"   🏢 公司: {user_info.get('brandName')}")

        # 3. 获取职位列表
        print("\n📍 步骤 3: 获取已沟通职位列表...")
        jobs_result = await automation.get_chatted_jobs()

        print("\n" + "=" * 70)
        print("职位列表结果:")
        print("=" * 70)
        print(f"成功: {jobs_result.get('success')}")
        print(f"消息: {jobs_result.get('message')}")
        print(f"总数: {jobs_result.get('total')}")

        # 4. 显示职位详情
        jobs = jobs_result.get('jobs', [])
        if jobs:
            print(f"\n共找到 {len(jobs)} 个职位：\n")
            for idx, job in enumerate(jobs, 1):
                print(f"职位 {idx}:")
                print(f"  📋 职位名称: {job.get('jobName')}")
                print(f"  💰 薪资: {job.get('salaryDesc')}")
                print(f"  📍 地址: {job.get('address')}")
                print(f"  🏷️  职位类型: {job.get('jobType')}")
                print(f"  🟢 在线状态: {job.get('jobOnlineStatus')}")
                print(f"  📝 描述: {job.get('description', '无')[:50]}...")
                print(f"  🔑 Job ID: {job.get('encryptJobId')}")
                print()
        else:
            print("\n暂无职位数据")

        # 5. 保持浏览器打开一段时间
        print("=" * 70)
        print("\n📍 步骤 4: 浏览器将保持打开 10 秒...")
        await asyncio.sleep(10)

    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        # 清理资源
        print("\n📍 步骤 5: 清理资源...")
        await automation.cleanup()
        print("✅ 清理完成")

    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_jobs_list())
