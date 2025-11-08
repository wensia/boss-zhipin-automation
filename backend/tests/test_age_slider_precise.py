"""
测试精确设置年龄滑块
通过反复拖动和读取，直到年龄达到目标值

实现策略：
1. 拖动滑块
2. 读取tooltip显示的当前年龄
3. 计算差距
4. 根据差距调整拖动距离
5. 反复迭代直到达到目标（或达到最大尝试次数）
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
    """
    读取当前年龄值

    返回: {"min": str, "max": str} 例如 {"min": "24", "max": "44"}
    """
    try:
        # 方法1: 使用简单的类选择器
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

        if values:
            logger.info(f"    当前年龄: {values['min']} - {values['max']}")
            return values

        # 方法2: 使用用户提供的完整选择器（作为备用）
        logger.warning("方法1失败，尝试方法2（完整选择器）")

        min_selector = "#headerWrap .filter-item.age .vue-slider-dot:nth-child(1) .vue-slider-dot-tooltip-text"
        max_selector = "#headerWrap .filter-item.age .vue-slider-dot:nth-child(3) .vue-slider-dot-tooltip-text"

        min_elem = await frame.query_selector(min_selector)
        max_elem = await frame.query_selector(max_selector)

        if min_elem and max_elem:
            min_val = await min_elem.text_content()
            max_val = await max_elem.text_content()

            values = {
                "min": min_val.strip(),
                "max": max_val.strip()
            }
            logger.info(f"    当前年龄（方法2）: {values['min']} - {values['max']}")
            return values

        return None

    except Exception as e:
        logger.error(f"读取年龄值失败: {e}")
        return None


async def set_age_precise(automation, frame, target_min: int, target_max: int = None, max_iterations: int = 10):
    """
    精确设置年龄范围（迭代调整直到达到目标）

    Args:
        automation: BossAutomation实例
        frame: iframe对象
        target_min: 目标最小年龄
        target_max: 目标最大年龄（None表示不限）
        max_iterations: 最大尝试次数

    Returns:
        {"success": bool, "actual_values": dict, "iterations": int}
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"🎯 目标年龄: {target_min} - {target_max if target_max else '不限'}")
    logger.info(f"{'='*80}")

    # 获取滑块信息
    slider_info = await frame.evaluate("""
    () => {
        const ageSection = document.querySelector('.filter-item.age');
        const slider = ageSection.querySelector('.vue-slider');
        const handles = ageSection.querySelectorAll('.vue-slider-dot');

        const sliderRect = slider.getBoundingClientRect();

        return {
            slider_x: sliderRect.left,
            slider_y: sliderRect.top + sliderRect.height / 2,
            slider_width: sliderRect.width,
            handles: Array.from(handles).map(h => {
                const rect = h.getBoundingClientRect();
                return {
                    x: rect.left + rect.width / 2,
                    y: rect.top + rect.height / 2
                };
            })
        };
    }
    """)

    logger.info(f"滑块信息:")
    logger.info(f"  位置: ({slider_info['slider_x']:.1f}, {slider_info['slider_y']:.1f})")
    logger.info(f"  宽度: {slider_info['slider_width']:.1f}px")
    logger.info(f"  手柄数量: {len(slider_info['handles'])}")

    # 假设年龄范围是16-60
    AGE_MIN = 16
    AGE_MAX = 60

    # ========================================
    # 调整最小年龄
    # ========================================
    logger.info(f"\n📍 调整最小年龄到 {target_min}")

    for iteration in range(max_iterations):
        logger.info(f"\n  迭代 {iteration + 1}/{max_iterations}:")

        # 读取当前值
        current = await read_age_values(frame)
        if not current:
            logger.error("    ❌ 无法读取当前年龄")
            break

        # 解析最小年龄
        try:
            current_min = int(current['min'])
        except:
            logger.warning(f"    无法解析最小年龄: {current['min']}")
            break

        # 检查是否达到目标
        if current_min == target_min:
            logger.info(f"    ✅ 已达到目标: {current_min}")
            break

        # 计算差距和调整距离
        diff = target_min - current_min
        logger.info(f"    差距: {diff} 岁")

        # 计算需要移动的像素距离
        # 每岁对应的像素: slider_width / (AGE_MAX - AGE_MIN)
        pixels_per_year = slider_info['slider_width'] / (AGE_MAX - AGE_MIN)
        move_distance = diff * pixels_per_year

        logger.info(f"    需要移动: {move_distance:.1f}px (每岁={pixels_per_year:.2f}px)")

        # 重新获取当前手柄位置（每次迭代都要重新获取）
        current_slider_info = await frame.evaluate("""
        () => {
            const ageSection = document.querySelector('.filter-item.age');
            if (!ageSection) return null;

            const handles = ageSection.querySelectorAll('.vue-slider-dot');
            if (handles.length < 1) return null;

            const rect = handles[0].getBoundingClientRect();
            return {
                x: rect.left + rect.width / 2,
                y: rect.top + rect.height / 2
            };
        }
        """)

        if not current_slider_info:
            logger.error("    ❌ 无法获取手柄位置")
            break

        # 拖动手柄
        current_x = current_slider_info['x']
        current_y = current_slider_info['y']
        target_x = current_x + move_distance

        logger.info(f"    拖动: ({current_x:.1f}, {current_y:.1f}) -> ({target_x:.1f}, {current_y:.1f})")

        await automation.page.mouse.move(current_x, current_y)
        await asyncio.sleep(0.2)
        await automation.page.mouse.down()
        await asyncio.sleep(0.1)
        await automation.page.mouse.move(target_x, current_y, steps=15)
        await asyncio.sleep(0.2)
        await automation.page.mouse.up()
        await asyncio.sleep(0.5)

        # 截图
        await automation.page.screenshot(
            path=str(SCREENSHOT_DIR / f"precise_min_iter{iteration + 1}.png")
        )

    # ========================================
    # 调整最大年龄（如果指定）
    # ========================================
    if target_max is not None:
        logger.info(f"\n📍 调整最大年龄到 {target_max}")

        for iteration in range(max_iterations):
            logger.info(f"\n  迭代 {iteration + 1}/{max_iterations}:")

            # 读取当前值
            current = await read_age_values(frame)
            if not current:
                logger.error("    ❌ 无法读取当前年龄")
                break

            # 解析最大年龄
            max_val = current['max']
            if max_val == '不限':
                current_max = AGE_MAX
            else:
                try:
                    current_max = int(max_val)
                except:
                    logger.warning(f"    无法解析最大年龄: {max_val}")
                    break

            # 检查是否达到目标
            if current_max == target_max:
                logger.info(f"    ✅ 已达到目标: {current_max}")
                break

            # 计算差距和调整距离
            diff = target_max - current_max
            logger.info(f"    差距: {diff} 岁")

            pixels_per_year = slider_info['slider_width'] / (AGE_MAX - AGE_MIN)
            move_distance = diff * pixels_per_year

            logger.info(f"    需要移动: {move_distance:.1f}px")

            # 获取当前手柄位置（最大年龄是第二个手柄）
            current_slider_info = await frame.evaluate("""
            () => {
                const ageSection = document.querySelector('.filter-item.age');
                if (!ageSection) return null;

                const handles = ageSection.querySelectorAll('.vue-slider-dot');
                if (handles.length < 2) return null;

                const handle = handles[handles.length - 1];  // 最后一个手柄
                const rect = handle.getBoundingClientRect();
                return {
                    x: rect.left + rect.width / 2,
                    y: rect.top + rect.height / 2
                };
            }
            """)

            if not current_slider_info:
                logger.error("    ❌ 无法获取手柄位置")
                break

            # 拖动手柄
            current_x = current_slider_info['x']
            current_y = current_slider_info['y']
            target_x = current_x + move_distance

            logger.info(f"    拖动: ({current_x:.1f}, {current_y:.1f}) -> ({target_x:.1f}, {current_y:.1f})")

            await automation.page.mouse.move(current_x, current_y)
            await asyncio.sleep(0.2)
            await automation.page.mouse.down()
            await asyncio.sleep(0.1)
            await automation.page.mouse.move(target_x, current_y, steps=15)
            await asyncio.sleep(0.2)
            await automation.page.mouse.up()
            await asyncio.sleep(0.5)

            # 截图
            await automation.page.screenshot(
                path=str(SCREENSHOT_DIR / f"precise_max_iter{iteration + 1}.png")
            )

    # 读取最终值
    final_values = await read_age_values(frame)

    logger.info(f"\n{'='*80}")
    logger.info(f"📊 最终结果")
    logger.info(f"{'='*80}")
    logger.info(f"目标: {target_min} - {target_max if target_max else '不限'}")
    logger.info(f"实际: {final_values['min']} - {final_values['max']}")

    # 判断是否成功
    success = False
    try:
        final_min = int(final_values['min'])
        final_max_str = final_values['max']

        if target_max is None:
            # 只检查最小年龄
            success = (final_min == target_min)
        else:
            # 检查两个值
            if final_max_str == '不限':
                final_max = AGE_MAX
            else:
                final_max = int(final_max_str)

            success = (final_min == target_min and final_max == target_max)
    except:
        success = False

    if success:
        logger.info("✅ 成功达到目标年龄！")
    else:
        logger.warning("⚠️ 未能精确达到目标年龄，但已尽力接近")

    return {
        "success": success,
        "actual_values": final_values,
        "target_values": {
            "min": target_min,
            "max": target_max
        }
    }


async def test_precise_age_setting():
    """测试精确设置年龄"""
    automation = BossAutomation()

    try:
        logger.info("=" * 80)
        logger.info("🎯 测试精确设置年龄（迭代调整）")
        logger.info("=" * 80)

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
        logger.info("✅ 筛选弹窗已打开")

        # 截图初始状态
        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "precise_00_initial.png"))

        # 读取初始年龄
        initial = await read_age_values(recommend_frame)
        logger.info(f"初始年龄: {initial['min']} - {initial['max']}")

        # ========================================
        # 测试1: 设置年龄为 25-35
        # ========================================
        logger.info("\n" + "=" * 80)
        logger.info("🧪 测试1: 设置年龄为 25-35")
        logger.info("=" * 80)

        result1 = await set_age_precise(
            automation,
            recommend_frame,
            target_min=25,
            target_max=35,
            max_iterations=10
        )

        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "precise_test1_final.png"))

        # ========================================
        # 测试2: 设置年龄为 30-45
        # ========================================
        logger.info("\n" + "=" * 80)
        logger.info("🧪 测试2: 设置年龄为 30-45")
        logger.info("=" * 80)

        result2 = await set_age_precise(
            automation,
            recommend_frame,
            target_min=30,
            target_max=45,
            max_iterations=10
        )

        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "precise_test2_final.png"))

        # ========================================
        # 测试3: 设置年龄为 22-不限
        # ========================================
        logger.info("\n" + "=" * 80)
        logger.info("🧪 测试3: 设置年龄为 22-不限")
        logger.info("=" * 80)

        result3 = await set_age_precise(
            automation,
            recommend_frame,
            target_min=22,
            target_max=None,
            max_iterations=10
        )

        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "precise_test3_final.png"))

        # ========================================
        # 总结
        # ========================================
        logger.info("\n" + "=" * 80)
        logger.info("📋 测试总结")
        logger.info("=" * 80)

        logger.info(f"\n测试1 (25-35): {'✅ 成功' if result1['success'] else '⚠️ 部分成功'}")
        logger.info(f"  实际: {result1['actual_values']['min']}-{result1['actual_values']['max']}")

        logger.info(f"\n测试2 (30-45): {'✅ 成功' if result2['success'] else '⚠️ 部分成功'}")
        logger.info(f"  实际: {result2['actual_values']['min']}-{result2['actual_values']['max']}")

        logger.info(f"\n测试3 (22-不限): {'✅ 成功' if result3['success'] else '⚠️ 部分成功'}")
        logger.info(f"  实际: {result3['actual_values']['min']}-{result3['actual_values']['max']}")

        logger.info("\n生成的截图:")
        logger.info("  precise_00_initial.png - 初始状态")
        logger.info("  precise_min_iter*.png - 最小年龄调整过程")
        logger.info("  precise_max_iter*.png - 最大年龄调整过程")
        logger.info("  precise_test*_final.png - 每个测试的最终状态")

        # 保持浏览器打开
        logger.info("\n⏳ 浏览器将保持打开 60 秒...")
        await asyncio.sleep(60)

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}", exc_info=True)

    finally:
        await automation.cleanup()


if __name__ == "__main__":
    asyncio.run(test_precise_age_setting())
