"""
筛选功能集成测试
测试完整的筛选流程：
1. 初始化浏览器
2. 登录
3. 选择职位
4. 应用筛选条件
"""

import asyncio
import sys
from app.services.boss_automation import BossAutomation
from app.models.filters import FilterOptions, AgeFilter
from app.utils.filters_applier import FiltersApplier


async def test_complete_filter_flow():
    """测试完整的筛选流程"""
    automation = BossAutomation()

    try:
        print("=" * 80)
        print("🚀 开始筛选功能集成测试")
        print("=" * 80)

        # 步骤 1: 初始化浏览器
        print("\n📦 步骤 1: 初始化浏览器...")
        await automation.initialize(headless=False)
        print("✅ 浏览器初始化成功")

        # 步骤 2: 检查登录状态
        print("\n🔐 步骤 2: 检查登录状态...")
        login_status = await automation.check_login_status()

        if not login_status.get('logged_in'):
            print("❌ 未登录，请先登录 Boss 直聘")

            # 获取二维码
            qr_result = await automation.get_qrcode()
            if qr_result.get('qrcode'):
                print(f"📱 请扫描二维码登录")
                print(f"二维码已显示在浏览器中")

                # 轮询登录状态（最多等待 2 分钟）
                for i in range(60):
                    await asyncio.sleep(2)
                    login_status = await automation.check_login_status()
                    if login_status.get('logged_in'):
                        print("✅ 登录成功")
                        break
                    if i % 10 == 0:
                        print(f"⏳ 等待登录... ({i * 2}s)")

                if not login_status.get('logged_in'):
                    print("❌ 登录超时，测试终止")
                    return
        else:
            user_info = login_status.get('user_info', {})
            print(f"✅ 已登录: {user_info.get('showName', 'Unknown')}")

        # 步骤 3: 获取并选择职位
        print("\n💼 步骤 3: 获取职位列表...")
        jobs_result = await automation.get_available_jobs()

        if not jobs_result.get('success') or not jobs_result.get('jobs'):
            print("❌ 未找到可用职位")
            return

        jobs = jobs_result.get('jobs', [])
        print(f"✅ 找到 {len(jobs)} 个职位")

        # 显示职位列表
        for idx, job in enumerate(jobs[:5], 1):
            print(f"   {idx}. {job['label']}")

        # 选择第一个职位
        selected_job = jobs[0]
        print(f"\n📌 选择职位: {selected_job['label']}")

        select_result = await automation.select_job_position(selected_job['value'])
        if not select_result.get('success'):
            print(f"❌ 职位选择失败: {select_result.get('message')}")
            return

        print("✅ 职位选择成功")

        # 步骤 4: 导航到推荐页面
        print("\n🔍 步骤 4: 导航到推荐页面...")
        await automation.navigate_to_recommend_page()
        await asyncio.sleep(3)
        print("✅ 已进入推荐页面")

        # 步骤 5: 获取 iframe
        print("\n🖼️  步骤 5: 定位推荐页面 iframe...")
        recommend_frame = None
        for frame in automation.page.frames:
            if frame.name == 'recommendFrame':
                recommend_frame = frame
                break

        if not recommend_frame:
            print("❌ 未找到推荐页面 iframe")
            return

        print("✅ 找到 recommendFrame")

        # 步骤 6: 创建测试筛选条件
        print("\n⚙️  步骤 6: 配置测试筛选条件...")

        # 配置多种筛选条件进行测试
        test_filters = FilterOptions(
            age=AgeFilter(min=25, max=35),
            gender="男",
            activity="今日活跃",
            experience="3-5年",
            education="本科",
            major=["计算机类", "电子信息类"],
            school=["985", "211"],
            keywords=["Python", "后端开发"]
        )

        print("📋 测试筛选条件:")
        print(f"   • 年龄: 25-35 岁")
        print(f"   • 性别: 男")
        print(f"   • 活跃度: 今日活跃")
        print(f"   • 经验: 3-5年")
        print(f"   • 学历: 本科")
        print(f"   • 专业: 计算机类, 电子信息类")
        print(f"   • 院校: 985, 211")
        print(f"   • 关键词: Python, 后端开发")

        # 步骤 7: 应用筛选条件
        print("\n🎯 步骤 7: 应用筛选条件...")
        applier = FiltersApplier(recommend_frame, automation.page)

        # 打开筛选面板
        print("   📂 打开筛选面板...")
        if not await applier.open_filter_panel():
            print("   ❌ 无法打开筛选面板")
            return
        print("   ✅ 筛选面板已打开")

        # 应用所有筛选条件
        print("   🔧 应用筛选条件...")
        filter_result = await applier.apply_all_filters(test_filters)

        # 显示结果
        print("\n" + "=" * 80)
        print("📊 筛选条件应用结果")
        print("=" * 80)

        if filter_result['success']:
            print(f"✅ 筛选条件应用成功")
            print(f"\n成功应用的筛选条件 ({len(filter_result['applied_filters'])} 项):")
            for f in filter_result['applied_filters']:
                print(f"   ✓ {f}")

            if filter_result['failed_filters']:
                print(f"\n失败的筛选条件 ({len(filter_result['failed_filters'])} 项):")
                for f in filter_result['failed_filters']:
                    print(f"   ✗ {f}")

            print(f"\n确认状态: {'✅ 已确认' if filter_result.get('confirmed') else '❌ 未确认'}")
        else:
            print(f"❌ 筛选条件应用失败")
            if 'error' in filter_result:
                print(f"错误信息: {filter_result['error']}")

        # 保持浏览器打开以便观察结果
        print("\n" + "=" * 80)
        print("🎉 测试完成！")
        print("=" * 80)
        print("\n浏览器将保持打开 30 秒，请观察筛选结果...")
        print("（检查推荐页面的候选人列表是否符合筛选条件）")

        await asyncio.sleep(30)

    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("\n🧹 清理资源...")
        await automation.cleanup()
        print("✅ 测试结束")


if __name__ == "__main__":
    print("筛选功能集成测试")
    print("=" * 80)
    asyncio.run(test_complete_filter_flow())
