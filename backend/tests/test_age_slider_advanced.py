#!/usr/bin/env python3
"""
年龄滑块高级测试 - 使用CDP和PointerEvent
深入测试vue-slider组件的各种交互方式
"""

import asyncio
import logging
from pathlib import Path
from app.services.boss_automation import BossAutomation

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)


async def read_age_values(frame) -> dict:
    """读取当前年龄值"""
    values = await frame.evaluate("""
    () => {
        const ageSection = document.querySelector('.filter-item.age');
        if (!ageSection) return null;

        const tooltips = ageSection.querySelectorAll('.vue-slider-dot-tooltip-text');
        if (tooltips.length >= 2) {
            return {
                min: tooltips[0].textContent.trim(),
                max: tooltips[1].textContent.trim()
            };
        }
        return null;
    }
    """)
    return values


async def test_method_1_pointer_events(automation, frame, page):
    """
    方法1: 使用dispatch_event发送PointerEvent
    """
    logger.info("\n" + "="*60)
    logger.info("方法1: 测试PointerEvent (dispatch_event)")
    logger.info("="*60)

    try:
        # 读取初始值
        initial = await read_age_values(frame)
        logger.info(f"初始年龄: {initial['min']} - {initial['max']}")

        # 获取滑块信息
        slider_info = await frame.evaluate("""
        () => {
            const slider = document.querySelector('.filter-item.age .vue-slider');
            const rect = slider.getBoundingClientRect();

            const handles = document.querySelectorAll('.filter-item.age .vue-slider-dot-handle');
            const leftHandle = handles[0];
            const leftRect = leftHandle.getBoundingClientRect();

            return {
                slider_x: rect.left,
                slider_y: rect.top,
                slider_width: rect.width,
                slider_height: rect.height,
                left_handle_x: leftRect.left + leftRect.width / 2,
                left_handle_y: leftRect.top + leftRect.height / 2
            };
        }
        """)

        logger.info(f"滑块信息: x={slider_info['slider_x']:.1f}, width={slider_info['slider_width']:.1f}")
        logger.info(f"左手柄位置: ({slider_info['left_handle_x']:.1f}, {slider_info['left_handle_y']:.1f})")

        # 计算目标位置（设置为25岁）
        AGE_MIN = 16
        AGE_MAX = 60
        target_age = 25
        percent = (target_age - AGE_MIN) / (AGE_MAX - AGE_MIN)
        target_x = slider_info['slider_x'] + slider_info['slider_width'] * percent
        target_y = slider_info['slider_y'] + slider_info['slider_height'] / 2

        logger.info(f"目标位置: ({target_x:.1f}, {target_y:.1f}) - 目标年龄: {target_age}")

        # 获取handle元素
        handles = await frame.query_selector_all('.vue-slider-dot-handle')
        left_handle = handles[0]

        # 发送PointerEvent序列
        logger.info("发送PointerEvent序列...")

        # 1. pointerenter
        await left_handle.dispatch_event('pointerenter', {
            'pointerId': 1,
            'pointerType': 'mouse',
            'isPrimary': True
        })
        await asyncio.sleep(0.2)

        # 2. pointerdown
        logger.info("  1. pointerdown")
        await left_handle.dispatch_event('pointerdown', {
            'button': 0,
            'buttons': 1,
            'clientX': slider_info['left_handle_x'],
            'clientY': slider_info['left_handle_y'],
            'pointerId': 1,
            'pointerType': 'mouse',
            'isPrimary': True,
            'pressure': 0.5
        })
        await asyncio.sleep(0.3)

        # 3. pointermove (多次)
        logger.info("  2. pointermove (10步)")
        steps = 10
        for i in range(steps + 1):
            progress = i / steps
            current_x = slider_info['left_handle_x'] + (target_x - slider_info['left_handle_x']) * progress

            await left_handle.dispatch_event('pointermove', {
                'clientX': current_x,
                'clientY': slider_info['left_handle_y'],
                'pointerId': 1,
                'pointerType': 'mouse',
                'isPrimary': True,
                'buttons': 1,
                'pressure': 0.5
            })
            await asyncio.sleep(0.05)

        # 4. pointerup
        logger.info("  3. pointerup")
        await left_handle.dispatch_event('pointerup', {
            'button': 0,
            'buttons': 0,
            'clientX': target_x,
            'clientY': target_y,
            'pointerId': 1,
            'pointerType': 'mouse',
            'isPrimary': True,
            'pressure': 0
        })
        await asyncio.sleep(0.2)

        # 5. pointerleave
        await left_handle.dispatch_event('pointerleave', {
            'pointerId': 1,
            'pointerType': 'mouse',
            'isPrimary': True
        })
        await asyncio.sleep(1)

        # 读取结果
        final = await read_age_values(frame)
        logger.info(f"最终年龄: {final['min']} - {final['max']}")

        success = final['min'] != initial['min']
        if success:
            logger.info("✅ 方法1成功！年龄已改变")
        else:
            logger.warning("❌ 方法1失败，年龄未改变")

        await page.screenshot(path=str(SCREENSHOT_DIR / "advanced_method1.png"), full_page=True)
        return success

    except Exception as e:
        logger.error(f"❌ 方法1出错: {e}")
        return False


async def test_method_2_cdp(automation, frame, page):
    """
    方法2: 使用CDP (Chrome DevTools Protocol)
    """
    logger.info("\n" + "="*60)
    logger.info("方法2: 测试CDP底层控制")
    logger.info("="*60)

    try:
        # 重置滑块（点击取消重新打开）
        logger.info("重置筛选面板...")
        cancel_btn = await frame.query_selector("text=取消")
        if cancel_btn:
            await cancel_btn.click()
            await asyncio.sleep(1)

        filter_btn = await frame.wait_for_selector(".recommend-filter", timeout=5000)
        await filter_btn.click()
        await asyncio.sleep(2)

        # 读取初始值
        initial = await read_age_values(frame)
        logger.info(f"初始年龄: {initial['min']} - {initial['max']}")

        # 获取滑块信息
        slider_info = await frame.evaluate("""
        () => {
            const handles = document.querySelectorAll('.filter-item.age .vue-slider-dot-handle');
            const leftHandle = handles[0];
            const leftRect = leftHandle.getBoundingClientRect();

            const slider = document.querySelector('.filter-item.age .vue-slider');
            const sliderRect = slider.getBoundingClientRect();

            return {
                left_handle_x: leftRect.left + leftRect.width / 2,
                left_handle_y: leftRect.top + leftRect.height / 2,
                slider_x: sliderRect.left,
                slider_width: sliderRect.width
            };
        }
        """)

        # 计算目标位置（30岁）
        AGE_MIN = 16
        AGE_MAX = 60
        target_age = 30
        percent = (target_age - AGE_MIN) / (AGE_MAX - AGE_MIN)
        target_x = slider_info['slider_x'] + slider_info['slider_width'] * percent

        logger.info(f"目标: {target_age}岁, 位置: ({target_x:.1f}, {slider_info['left_handle_y']:.1f})")

        # 获取CDP会话
        logger.info("创建CDP会话...")
        cdp = await page.context.new_cdp_session(page)

        # 发送CDP鼠标事件
        logger.info("发送CDP鼠标事件...")

        # 1. mousePressed
        logger.info("  1. mousePressed")
        await cdp.send('Input.dispatchMouseEvent', {
            'type': 'mousePressed',
            'x': slider_info['left_handle_x'],
            'y': slider_info['left_handle_y'],
            'button': 'left',
            'clickCount': 1
        })
        await asyncio.sleep(0.3)

        # 2. mouseMoved (多步)
        logger.info("  2. mouseMoved (15步)")
        steps = 15
        for i in range(steps + 1):
            progress = i / steps
            current_x = slider_info['left_handle_x'] + (target_x - slider_info['left_handle_x']) * progress

            await cdp.send('Input.dispatchMouseEvent', {
                'type': 'mouseMoved',
                'x': current_x,
                'y': slider_info['left_handle_y'],
                'button': 'left'
            })
            await asyncio.sleep(0.05)

        # 3. mouseReleased
        logger.info("  3. mouseReleased")
        await cdp.send('Input.dispatchMouseEvent', {
            'type': 'mouseReleased',
            'x': target_x,
            'y': slider_info['left_handle_y'],
            'button': 'left',
            'clickCount': 1
        })
        await asyncio.sleep(1)

        # 读取结果
        final = await read_age_values(frame)
        logger.info(f"最终年龄: {final['min']} - {final['max']}")

        success = final['min'] != initial['min']
        if success:
            logger.info("✅ 方法2成功！年龄已改变")
        else:
            logger.warning("❌ 方法2失败，年龄未改变")

        await page.screenshot(path=str(SCREENSHOT_DIR / "advanced_method2.png"), full_page=True)
        return success

    except Exception as e:
        logger.error(f"❌ 方法2出错: {e}")
        return False


async def test_method_3_vue_component(automation, frame, page):
    """
    方法3: 直接操作Vue组件实例
    """
    logger.info("\n" + "="*60)
    logger.info("方法3: 直接操作Vue组件实例")
    logger.info("="*60)

    try:
        # 重置
        logger.info("重置筛选面板...")
        cancel_btn = await frame.query_selector("text=取消")
        if cancel_btn:
            await cancel_btn.click()
            await asyncio.sleep(1)

        filter_btn = await frame.wait_for_selector(".recommend-filter", timeout=5000)
        await filter_btn.click()
        await asyncio.sleep(2)

        initial = await read_age_values(frame)
        logger.info(f"初始年龄: {initial['min']} - {initial['max']}")

        # 尝试访问Vue实例
        logger.info("检查Vue实例...")
        vue_check = await frame.evaluate("""
        () => {
            const slider = document.querySelector('.filter-item.age .vue-slider');

            return {
                hasVue2: !!slider.__vue__,
                hasVue3: !!slider.__vueParentComponent,
                vue2Keys: slider.__vue__ ? Object.keys(slider.__vue__).slice(0, 20) : [],
                vue3Keys: slider.__vueParentComponent ? Object.keys(slider.__vueParentComponent).slice(0, 20) : []
            };
        }
        """)

        logger.info(f"Vue2实例存在: {vue_check['hasVue2']}")
        logger.info(f"Vue3实例存在: {vue_check['hasVue3']}")

        if vue_check['hasVue2']:
            logger.info(f"Vue2属性: {vue_check['vue2Keys'][:10]}")
        if vue_check['hasVue3']:
            logger.info(f"Vue3属性: {vue_check['vue3Keys'][:10]}")

        # 尝试直接设置值
        logger.info("尝试直接设置年龄为 [28, 45]...")

        result = await frame.evaluate("""
        (params) => {
            const slider = document.querySelector('.filter-item.age .vue-slider');
            const logs = [];

            try {
                // Vue 2
                if (slider.__vue__) {
                    logs.push('找到Vue2实例');

                    // 尝试多种方式
                    const component = slider.__vue__;

                    // 方式1: 直接设置value
                    if (component.value !== undefined) {
                        logs.push('尝试设置value属性');
                        component.value = [params.min, params.max];
                    }

                    // 方式2: 调用方法
                    if (typeof component.setValue === 'function') {
                        logs.push('调用setValue方法');
                        component.setValue([params.min, params.max]);
                    }

                    // 方式3: 触发事件
                    if (component.$emit) {
                        logs.push('触发input事件');
                        component.$emit('input', [params.min, params.max]);
                        component.$emit('change', [params.min, params.max]);
                    }

                    return { success: true, method: 'vue2', logs };
                }

                // Vue 3
                if (slider.__vueParentComponent) {
                    logs.push('找到Vue3实例');
                    const component = slider.__vueParentComponent;

                    if (component.emit) {
                        logs.push('触发update:modelValue事件');
                        component.emit('update:modelValue', [params.min, params.max]);
                    }

                    return { success: true, method: 'vue3', logs };
                }

                logs.push('未找到Vue实例');
                return { success: false, logs };

            } catch (error) {
                logs.push('错误: ' + error.message);
                return { success: false, error: error.message, logs };
            }
        }
        """, {'min': 28, 'max': 45})

        logger.info(f"Vue操作结果: {result}")
        for log in result.get('logs', []):
            logger.info(f"  - {log}")

        await asyncio.sleep(1)

        # 读取结果
        final = await read_age_values(frame)
        logger.info(f"最终年龄: {final['min']} - {final['max']}")

        success = final['min'] != initial['min']
        if success:
            logger.info("✅ 方法3成功！年龄已改变")
        else:
            logger.warning("❌ 方法3失败，年龄未改变")

        await page.screenshot(path=str(SCREENSHOT_DIR / "advanced_method3.png"), full_page=True)
        return success

    except Exception as e:
        logger.error(f"❌ 方法3出错: {e}")
        return False


async def test_method_4_keyboard(automation, frame, page):
    """
    方法4: 使用键盘方向键
    """
    logger.info("\n" + "="*60)
    logger.info("方法4: 使用键盘方向键")
    logger.info("="*60)

    try:
        # 重置
        logger.info("重置筛选面板...")
        cancel_btn = await frame.query_selector("text=取消")
        if cancel_btn:
            await cancel_btn.click()
            await asyncio.sleep(1)

        filter_btn = await frame.wait_for_selector(".recommend-filter", timeout=5000)
        await filter_btn.click()
        await asyncio.sleep(2)

        initial = await read_age_values(frame)
        logger.info(f"初始年龄: {initial['min']} - {initial['max']}")

        # 获取左侧手柄
        handles = await frame.query_selector_all('.vue-slider-dot-handle')
        left_handle = handles[0]

        # Focus到手柄
        logger.info("Focus到左侧手柄...")
        await left_handle.focus()
        await asyncio.sleep(0.5)

        # 按右方向键（增加年龄）
        logger.info("按ArrowRight键 20次...")
        for i in range(20):
            await page.keyboard.press('ArrowRight')
            await asyncio.sleep(0.1)

        await asyncio.sleep(1)

        # 读取结果
        final = await read_age_values(frame)
        logger.info(f"最终年龄: {final['min']} - {final['max']}")

        success = final['min'] != initial['min']
        if success:
            logger.info("✅ 方法4成功！年龄已改变")
        else:
            logger.warning("❌ 方法4失败，年龄未改变")

        await page.screenshot(path=str(SCREENSHOT_DIR / "advanced_method4.png"), full_page=True)
        return success

    except Exception as e:
        logger.error(f"❌ 方法4出错: {e}")
        return False


async def main():
    """主函数"""
    automation = BossAutomation()

    try:
        logger.info("="*80)
        logger.info("🚀 年龄滑块高级测试 - CDP & PointerEvent & Vue & Keyboard")
        logger.info("="*80)

        # 初始化
        await automation.initialize(headless=False)
        await asyncio.sleep(2)

        # 登录检查
        login_status = await automation.check_login_status()
        if not login_status.get('logged_in'):
            logger.error("❌ 未登录")
            return

        logger.info("✅ 已登录")

        # 导航到推荐页面
        await automation.navigate_to_recommend_page()
        await asyncio.sleep(3)

        # 获取iframe
        recommend_frame = None
        for frame in automation.page.frames:
            if frame.name == 'recommendFrame':
                recommend_frame = frame
                break

        if not recommend_frame:
            logger.error("❌ 未找到 recommendFrame iframe")
            return

        logger.info("✅ 找到 recommendFrame")

        # 打开筛选弹窗
        filter_btn = await recommend_frame.wait_for_selector(".recommend-filter", timeout=10000)
        await filter_btn.click()
        await asyncio.sleep(2)

        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "advanced_initial.png"), full_page=True)
        logger.info("✅ 筛选面板已打开")

        # 测试所有方法
        results = {}

        results['method1_pointer'] = await test_method_1_pointer_events(automation, recommend_frame, automation.page)
        results['method2_cdp'] = await test_method_2_cdp(automation, recommend_frame, automation.page)
        results['method3_vue'] = await test_method_3_vue_component(automation, recommend_frame, automation.page)
        results['method4_keyboard'] = await test_method_4_keyboard(automation, recommend_frame, automation.page)

        # 总结
        logger.info("\n" + "="*80)
        logger.info("📊 测试结果总结")
        logger.info("="*80)
        logger.info(f"方法1 (PointerEvent):  {'✅ 成功' if results['method1_pointer'] else '❌ 失败'}")
        logger.info(f"方法2 (CDP):           {'✅ 成功' if results['method2_cdp'] else '❌ 失败'}")
        logger.info(f"方法3 (Vue组件):       {'✅ 成功' if results['method3_vue'] else '❌ 失败'}")
        logger.info(f"方法4 (键盘):          {'✅ 成功' if results['method4_keyboard'] else '❌ 失败'}")
        logger.info("="*80)

        success_count = sum(1 for v in results.values() if v)
        logger.info(f"\n成功方法数: {success_count}/4")

        if success_count > 0:
            logger.info("🎉 找到可行的方法！")
        else:
            logger.warning("😞 所有方法都失败了")

        # 保持页面打开
        logger.info("\n按 Ctrl+C 退出...")
        await asyncio.sleep(300)

    except KeyboardInterrupt:
        logger.info("👋 用户中断")
    except Exception as e:
        logger.exception(f"❌ 测试出错: {e}")
    finally:
        logger.info("🛑 关闭浏览器...")
        await automation.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
