"""
通过 API 测试登录流程
"""
import requests
import time

# API 基础 URL
BASE_URL = "http://localhost:27421"


def test_login_via_api():
    """通过 API 测试登录"""
    print("=" * 60)
    print("通过 API 测试 Boss 直聘登录")
    print("=" * 60)

    # 1. 检查后端健康状态
    print("\n📍 步骤 1: 检查后端服务状态...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print(f"✅ 后端服务正常: {response.json()['message']}")
        else:
            print(f"❌ 后端服务异常: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 无法连接到后端服务: {e}")
        return

    # 2. 检查自动化服务状态
    print("\n📍 步骤 2: 检查自动化服务状态...")
    try:
        response = requests.get(f"{BASE_URL}/api/automation/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   服务已初始化: {status['service_initialized']}")
            print(f"   登录状态: {status['is_logged_in']}")
            if status['current_task_id']:
                print(f"   当前任务 ID: {status['current_task_id']}")
        else:
            print(f"❌ 获取状态失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 获取状态失败: {e}")

    # 3. 触发登录
    print("\n📍 步骤 3: 触发登录流程...")
    print("⚠️  浏览器窗口将会打开，请在浏览器中完成登录操作")
    print("⚠️  注意：请选择「我要招聘」选项卡")
    print("⚠️  等待页面跳转到 /web/boss/ 路径后，登录状态会自动保存")

    try:
        response = requests.post(f"{BASE_URL}/api/automation/login", timeout=180)
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 登录结果: {result['message']}")
            print(f"   登录状态: {'已登录' if result['logged_in'] else '未登录'}")
        else:
            print(f"❌ 登录失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
    except requests.exceptions.Timeout:
        print("⏱️  请求超时，请检查是否在浏览器中完成了登录")
    except Exception as e:
        print(f"❌ 登录失败: {e}")

    # 4. 再次检查登录状态
    print("\n📍 步骤 4: 验证登录状态...")
    try:
        response = requests.get(f"{BASE_URL}/api/automation/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   最终登录状态: {status['is_logged_in']}")
        else:
            print(f"❌ 获取状态失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 获取状态失败: {e}")

    # 5. 检查系统配置中的登录信息
    print("\n📍 步骤 5: 检查系统配置...")
    try:
        response = requests.get(f"{BASE_URL}/api/config")
        if response.status_code == 200:
            config = response.json()
            print(f"   Session 已保存: {config['boss_session_saved']}")
            if config['boss_username']:
                print(f"   用户名: {config['boss_username']}")
        else:
            print(f"❌ 获取配置失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 获取配置失败: {e}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    print("\n💡 提示:")
    print("   - 如果登录成功，登录状态会保存到 boss_auth.json 文件")
    print("   - 下次启动时会自动加载登录状态，无需重新登录")
    print("   - 可以通过前端界面（http://localhost:13601）查看详细状态")


if __name__ == "__main__":
    test_login_via_api()
