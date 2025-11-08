#!/usr/bin/env python3
"""
测试年龄滑块 - 使用Locator方法
根据用户建议的方法测试
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


async def inspect_slider_elements(frame, page):
    """检查滑块相关元素"""
    logger.info("🔍 检查滑块元素...")

    # 检查各种可能的类名
    element_checks = await frame.evaluate("""
    () => {
        const ageSection = document.querySelector('.filter-item.age');
        if (!ageSection) return {error: '未找到age容器'};

        return {
            slider_handle: ageSection.querySelectorAll('.slider-handle').length,
            vue_slider_dot: ageSection.querySelectorAll('.vue-slider-dot').length,
            vue_slider_dot_handle: ageSection.querySelectorAll('.vue-slider-dot-handle').length,
            all_classes: Array.from(ageSection.querySelectorAll('*'))
                .map(el => el.className)
                .filter(c => c && c.includes('handle') || c.includes('dot'))
                .slice(0, 10)
        };
    }
    """)

    logger.info(f"  .slider-handle 数量: {element_checks.get('slider_handle', 0)}")
    logger.info(f"  .vue-slider-dot 数量: {element_checks.get('vue_slider_dot', 0)}")
    logger.info(f"  .vue-slider-dot-handle 数量: {element_checks.get('vue_slider_dot_handle', 0)}")
    logger.info(f"  包含'handle'或'dot'的类名: {element_checks.get('all_classes', [])}")

    # 截图
    await page.screenshot(path="backend/screenshots/locator_inspect_elements.png", full_page=True)

    return element_checks


async def test_locator_drag_method(automation, frame, page, target_min: int = 23, target_max: int = 35):
    """
    使用用户建议的locator方法测试拖拽

    Args:
        target_min: 目标最小年龄（例如23）
        target_max: 目标最大年龄（例如35）
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"测试locator拖拽方法：设置年龄为 {target_min}-{target_max}")
    logger.info(f"{'='*60}\n")

    AGE_MIN = 16
    AGE_MAX = 60

    # 1. 先检查元素
    element_info = await inspect_slider_elements(frame, page)

    # 2. 读取初始值
    initial_values = await read_age_values(frame)
    logger.info(f"初始年龄: {initial_values['min']} - {initial_values['max']}")

    # 3. 获取滑块容器的bounding box
    slider_info = await frame.evaluate("""
    () => {
        const slider = document.querySelector('.filter-item.age .vue-slider');
        if (!slider) return null;

        const rect = slider.getBoundingClientRect();
        return {
            x: rect.left,
            y: rect.top,
            width: rect.width,
            height: rect.height
        };
    }
    """)

    if not slider_info:
        logger.error("❌ 未找到滑块容器")
        return False

    logger.info(f"滑块容器位置: x={slider_info['x']:.1f}, y={slider_info['y']:.1f}, width={slider_info['width']:.1f}")

    # 4. 尝试使用用户建议的方法
    # 首先检查是否有 .slider-handle
    if element_info.get('slider_handle', 0) > 0:
        logger.info("✅ 找到 .slider-handle 元素，使用用户建议的方法")
        handle_selector = '.slider-handle'
    elif element_info.get('vue_slider_dot_handle', 0) > 0:
        logger.info("✅ 找到 .vue-slider-dot-handle 元素")
        handle_selector = '.vue-slider-dot-handle'
    else:
        logger.info("⚠️  未找到 .slider-handle，使用 .vue-slider-dot")
        handle_selector = '.vue-slider-dot'

    # 5. 获取左侧手柄（最小年龄）
    left_handle_info = await frame.evaluate(f"""
    () => {{
        const ageSection = document.querySelector('.filter-item.age');
        const handles = ageSection.querySelectorAll('{handle_selector}');
        if (handles.length < 1) return null;

        const rect = handles[0].getBoundingClientRect();
        return {{
            x: rect.left + rect.width / 2,
            y: rect.top + rect.height / 2,
            width: rect.width,
            height: rect.height
        }};
    }}
    """)

    if not left_handle_info:
        logger.error("❌ 未找到左侧手柄")
        return False

    logger.info(f"左侧手柄位置: ({left_handle_info['x']:.1f}, {left_handle_info['y']:.1f})")

    # 6. 计算目标位置（设置最小年龄）
    target_percent_min = (target_min - AGE_MIN) / (AGE_MAX - AGE_MIN)
    target_x_min = slider_info['x'] + slider_info['width'] * target_percent_min
    target_y = slider_info['y'] + slider_info['height'] / 2

    logger.info(f"目标位置（最小年龄{target_min}）: x={target_x_min:.1f} (百分比: {target_percent_min:.1%})")

    # 7. 使用用户建议的方法拖拽左侧手柄
    logger.info("🎯 开始拖拽左侧手柄...")
    logger.info("  步骤1: hover到手柄")
    await page.mouse.move(left_handle_info['x'], left_handle_info['y'])
    await asyncio.sleep(0.5)

    logger.info("  步骤2: mouse.down()")
    await page.mouse.down()
    await asyncio.sleep(0.3)

    logger.info(f"  步骤3: mouse.move() 到 ({target_x_min:.1f}, {target_y:.1f})")
    await page.mouse.move(target_x_min, target_y, steps=20)
    await asyncio.sleep(0.3)

    logger.info("  步骤4: mouse.up()")
    await page.mouse.up()
    await asyncio.sleep(1)

    # 8. 读取第一次拖拽后的值
    after_min_values = await read_age_values(frame)
    logger.info(f"设置最小年龄后: {after_min_values['min']} - {after_min_values['max']}")

    # 截图
    await page.screenshot(path="backend/screenshots/locator_after_min.png", full_page=True)

    # 9. 获取右侧手柄（最大年龄）
    right_handle_info = await frame.evaluate(f"""
    () => {{
        const ageSection = document.querySelector('.filter-item.age');
        const handles = ageSection.querySelectorAll('{handle_selector}');
        if (handles.length < 2) return null;

        const rect = handles[1].getBoundingClientRect();
        return {{
            x: rect.left + rect.width / 2,
            y: rect.top + rect.height / 2
        }};
    }}
    """)

    if not right_handle_info:
        logger.error("❌ 未找到右侧手柄")
        return False

    logger.info(f"\n右侧手柄位置: ({right_handle_info['x']:.1f}, {right_handle_info['y']:.1f})")

    # 10. 计算目标位置（设置最大年龄）
    target_percent_max = (target_max - AGE_MIN) / (AGE_MAX - AGE_MIN)
    target_x_max = slider_info['x'] + slider_info['width'] * target_percent_max

    logger.info(f"目标位置（最大年龄{target_max}）: x={target_x_max:.1f} (百分比: {target_percent_max:.1%})")

    # 11. 拖拽右侧手柄
    logger.info("🎯 开始拖拽右侧手柄...")
    logger.info("  步骤1: hover到手柄")
    await page.mouse.move(right_handle_info['x'], right_handle_info['y'])
    await asyncio.sleep(0.5)

    logger.info("  步骤2: mouse.down()")
    await page.mouse.down()
    await asyncio.sleep(0.3)

    logger.info(f"  步骤3: mouse.move() 到 ({target_x_max:.1f}, {target_y:.1f})")
    await page.mouse.move(target_x_max, target_y, steps=20)
    await asyncio.sleep(0.3)

    logger.info("  步骤4: mouse.up()")
    await page.mouse.up()
    await asyncio.sleep(1)

    # 12. 读取最终值
    final_values = await read_age_values(frame)
    logger.info(f"\n{'='*60}")
    logger.info(f"最终年龄: {final_values['min']} - {final_values['max']}")
    logger.info(f"目标年龄: {target_min} - {target_max}")

    # 13. 验证结果
    min_match = final_values['min'] == str(target_min)
    max_match = final_values['max'] == str(target_max)
    success = min_match and max_match

    if success:
        logger.info("✅ 成功！年龄设置完全匹配")
    else:
        logger.warning(f"⚠️  部分匹配: 最小年龄{'✅' if min_match else '❌'}, 最大年龄{'✅' if max_match else '❌'}")

    logger.info(f"{'='*60}\n")

    # 最终截图
    await page.screenshot(path="backend/screenshots/locator_final.png", full_page=True)

    return success


async def main():
    """主函数"""
    automation = BossAutomation()

    try:
        logger.info("🚀 启动浏览器...")
        await automation.initialize(headless=False)
        await asyncio.sleep(2)

        logger.info("📱 检查登录状态...")
        login_status = await automation.check_login_status()
        if not login_status.get('logged_in'):
            logger.error("❌ 未登录")
            return

        logger.info("✅ 已登录")

        logger.info("🔍 导航到推荐页面...")
        await automation.navigate_to_recommend_page()
        await asyncio.sleep(3)

        # 获取推荐页面的iframe
        recommend_frame = None
        for frame in automation.page.frames:
            if frame.name == 'recommendFrame':
                recommend_frame = frame
                break

        if not recommend_frame:
            logger.error("❌ 未找到recommendFrame")
            return

        logger.info("✅ 找到recommendFrame")

        # 点击筛选按钮
        logger.info("🖱️  点击筛选按钮...")
        filter_btn = await recommend_frame.wait_for_selector(
            ".recommend-filter",
            timeout=10000
        )
        await filter_btn.click()
        await asyncio.sleep(2)

        # 截图筛选面板
        await automation.page.screenshot(
            path="backend/screenshots/locator_filter_panel.png",
            full_page=True
        )
        logger.info("✅ 筛选面板已打开")

        # 测试locator方法
        success = await test_locator_drag_method(
            automation,
            recommend_frame,
            automation.page,
            target_min=23,
            target_max=35
        )

        if success:
            logger.info("🎉 测试成功！")
        else:
            logger.info("📝 测试完成，请查看结果")

        # 保持页面打开以便查看
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
