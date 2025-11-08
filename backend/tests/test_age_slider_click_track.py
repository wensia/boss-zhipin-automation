"""
测试点击轨道方案设置年龄滑块
验证最小年龄和最大年龄的精确设置

测试策略：
1. 点击轨道的计算位置来设置年龄
2. 读取tooltip显示的实际年龄
3. 校验与目标年龄的差异
4. 测试多组不同的年龄组合
5. 分析精度和成功率
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

    Returns:
        {"min": str, "max": str} 例如 {"min": "24", "max": "44"}
    """
    try:
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
            logger.info(f"      当前年龄: {values['min']} - {values['max']}")
            return values

        return None

    except Exception as e:
        logger.error(f"读取年龄值失败: {e}")
        return None


async def click_track_to_set_age(page, frame, target_age: int, age_min: int = 16, age_max: int = 60):
    """
    通过点击轨道设置年龄

    Args:
        page: Page对象
        frame: iframe对象
        target_age: 目标年龄
        age_min: 年龄范围最小值
        age_max: 年龄范围最大值（"不限"对应的值）

    Returns:
        dict: {"success": bool, "actual": str, "target": int, "error": int}
    """
    try:
        # 获取滑块轨道信息
        track_info = await frame.evaluate("""
        () => {
            const ageSection = document.querySelector('.filter-item.age');
            if (!ageSection) return null;

            const slider = ageSection.querySelector('.vue-slider');
            if (!slider) return null;

            const rect = slider.getBoundingClientRect();
            return {
                x: rect.left,
                y: rect.top + rect.height / 2,
                width: rect.width,
                height: rect.height
            };
        }
        """)

        if not track_info:
            logger.error("    ❌ 未找到滑块轨道")
            return {"success": False, "error": "未找到轨道"}

        # 计算点击位置（百分比）
        percent = (target_age - age_min) / (age_max - age_min)
        click_x = track_info['x'] + track_info['width'] * percent
        click_y = track_info['y']

        logger.info(f"    点击轨道设置年龄为 {target_age}")
        logger.info(f"      百分比: {percent:.2%}")
        logger.info(f"      点击位置: ({click_x:.1f}, {click_y:.1f})")
        logger.info(f"      轨道范围: x={track_info['x']:.1f}, width={track_info['width']:.1f}")

        # 点击轨道
        await page.mouse.click(click_x, click_y)
        await asyncio.sleep(1)  # 等待滑块更新

        # 读取实际设置的值
        actual_values = await read_age_values(frame)

        if not actual_values:
            return {"success": False, "error": "无法读取年龄值"}

        # 判断点击影响了哪个手柄（最小还是最大年龄）
        # 这里我们需要判断最近的手柄
        actual_min = actual_values['min']
        actual_max = actual_values['max']

        # 尝试解析为整数
        try:
            actual_min_int = int(actual_min)
        except:
            actual_min_int = age_min

        try:
            if actual_max == '不限':
                actual_max_int = age_max
            else:
                actual_max_int = int(actual_max)
        except:
            actual_max_int = age_max

        # 判断哪个值改变了
        min_diff = abs(actual_min_int - target_age)
        max_diff = abs(actual_max_int - target_age)

        if min_diff < max_diff:
            # 最小年龄被改变了
            actual_value = actual_min
            error = target_age - actual_min_int
            logger.info(f"      ✅ 最小年龄设置为: {actual_value} (目标: {target_age}, 误差: {error})")
        else:
            # 最大年龄被改变了
            actual_value = actual_max
            error = target_age - actual_max_int
            logger.info(f"      ✅ 最大年龄设置为: {actual_value} (目标: {target_age}, 误差: {error})")

        return {
            "success": True,
            "actual": actual_value,
            "target": target_age,
            "error": error,
            "values": actual_values
        }

    except Exception as e:
        logger.error(f"    ❌ 点击轨道失败: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


async def set_age_range_by_clicking(page, frame, target_min: int, target_max: int = None,
                                     age_min: int = 16, age_max: int = 60):
    """
    通过点击轨道设置年龄范围

    Args:
        target_min: 目标最小年龄
        target_max: 目标最大年龄（None表示不限）

    Returns:
        dict: 测试结果
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"🎯 目标年龄范围: {target_min} - {target_max if target_max else '不限'}")
    logger.info(f"{'='*80}")

    results = {
        "target_min": target_min,
        "target_max": target_max,
        "success": False,
        "min_result": None,
        "max_result": None
    }

    # 步骤1: 设置最小年龄
    logger.info(f"\n📍 步骤1: 设置最小年龄为 {target_min}")
    min_result = await click_track_to_set_age(page, frame, target_min, age_min, age_max)
    results["min_result"] = min_result

    await asyncio.sleep(0.5)

    # 步骤2: 设置最大年龄（如果指定）
    if target_max is not None:
        logger.info(f"\n📍 步骤2: 设置最大年龄为 {target_max}")
        max_result = await click_track_to_set_age(page, frame, target_max, age_min, age_max)
        results["max_result"] = max_result

        await asyncio.sleep(0.5)

    # 步骤3: 读取最终值
    logger.info(f"\n📊 最终结果:")
    final_values = await read_age_values(frame)

    if final_values:
        results["final_values"] = final_values
        results["success"] = True

        logger.info(f"  目标: {target_min} - {target_max if target_max else '不限'}")
        logger.info(f"  实际: {final_values['min']} - {final_values['max']}")

        # 计算误差
        try:
            actual_min = int(final_values['min'])
            min_error = actual_min - target_min
            logger.info(f"  最小年龄误差: {min_error} 岁")

            if target_max is not None:
                if final_values['max'] == '不限':
                    actual_max = age_max
                else:
                    actual_max = int(final_values['max'])

                max_error = actual_max - target_max
                logger.info(f"  最大年龄误差: {max_error} 岁")

                # 判断是否成功
                if min_error == 0 and max_error == 0:
                    logger.info(f"  ✅ 完全精确！")
                    results["accuracy"] = "perfect"
                elif abs(min_error) <= 1 and abs(max_error) <= 1:
                    logger.info(f"  ✅ 误差在±1岁内，可接受")
                    results["accuracy"] = "acceptable"
                else:
                    logger.info(f"  ⚠️ 误差较大")
                    results["accuracy"] = "poor"
            else:
                # 只设置最小年龄
                if min_error == 0:
                    logger.info(f"  ✅ 完全精确！")
                    results["accuracy"] = "perfect"
                elif abs(min_error) <= 1:
                    logger.info(f"  ✅ 误差在±1岁内，可接受")
                    results["accuracy"] = "acceptable"
                else:
                    logger.info(f"  ⚠️ 误差较大")
                    results["accuracy"] = "poor"

        except Exception as e:
            logger.error(f"  ❌ 计算误差失败: {e}")
            results["accuracy"] = "unknown"

    return results


async def test_click_track_method():
    """测试点击轨道方案"""
    automation = BossAutomation()

    try:
        logger.info("=" * 80)
        logger.info("🎯 测试点击轨道方案设置年龄")
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
        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "click_track_00_initial.png"))

        # 读取初始年龄
        initial = await read_age_values(recommend_frame)
        logger.info(f"初始年龄: {initial['min']} - {initial['max']}")

        # ========================================
        # 测试1: 设置年龄为 25 岁
        # ========================================
        logger.info("\n" + "=" * 80)
        logger.info("🧪 测试1: 只点击一次，设置为 25 岁")
        logger.info("=" * 80)

        result1 = await click_track_to_set_age(automation.page, recommend_frame, 25)

        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "click_track_01_single_25.png"))
        await asyncio.sleep(1)

        # ========================================
        # 重置：关闭并重新打开筛选框
        # ========================================
        logger.info("\n📍 重置筛选...")
        cancel_btn = await recommend_frame.query_selector("text=取消")
        if cancel_btn:
            await cancel_btn.click()
            await asyncio.sleep(1)

        filter_btn = await recommend_frame.wait_for_selector(".recommend-filter", timeout=10000)
        await filter_btn.click()
        await asyncio.sleep(2)

        # ========================================
        # 测试2: 设置年龄范围 22-35
        # ========================================
        logger.info("\n" + "=" * 80)
        logger.info("🧪 测试2: 设置年龄范围 22-35")
        logger.info("=" * 80)

        result2 = await set_age_range_by_clicking(
            automation.page,
            recommend_frame,
            target_min=22,
            target_max=35
        )

        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "click_track_02_range_22_35.png"))
        await asyncio.sleep(1)

        # ========================================
        # 重置
        # ========================================
        logger.info("\n📍 重置筛选...")
        cancel_btn = await recommend_frame.query_selector("text=取消")
        if cancel_btn:
            await cancel_btn.click()
            await asyncio.sleep(1)

        filter_btn = await recommend_frame.wait_for_selector(".recommend-filter", timeout=10000)
        await filter_btn.click()
        await asyncio.sleep(2)

        # ========================================
        # 测试3: 设置年龄范围 28-45
        # ========================================
        logger.info("\n" + "=" * 80)
        logger.info("🧪 测试3: 设置年龄范围 28-45")
        logger.info("=" * 80)

        result3 = await set_age_range_by_clicking(
            automation.page,
            recommend_frame,
            target_min=28,
            target_max=45
        )

        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "click_track_03_range_28_45.png"))
        await asyncio.sleep(1)

        # ========================================
        # 重置
        # ========================================
        logger.info("\n📍 重置筛选...")
        cancel_btn = await recommend_frame.query_selector("text=取消")
        if cancel_btn:
            await cancel_btn.click()
            await asyncio.sleep(1)

        filter_btn = await recommend_frame.wait_for_selector(".recommend-filter", timeout=10000)
        await filter_btn.click()
        await asyncio.sleep(2)

        # ========================================
        # 测试4: 设置年龄范围 30-50
        # ========================================
        logger.info("\n" + "=" * 80)
        logger.info("🧪 测试4: 设置年龄范围 30-50")
        logger.info("=" * 80)

        result4 = await set_age_range_by_clicking(
            automation.page,
            recommend_frame,
            target_min=30,
            target_max=50
        )

        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "click_track_04_range_30_50.png"))
        await asyncio.sleep(1)

        # ========================================
        # 重置
        # ========================================
        logger.info("\n📍 重置筛选...")
        cancel_btn = await recommend_frame.query_selector("text=取消")
        if cancel_btn:
            await cancel_btn.click()
            await asyncio.sleep(1)

        filter_btn = await recommend_frame.wait_for_selector(".recommend-filter", timeout=10000)
        await filter_btn.click()
        await asyncio.sleep(2)

        # ========================================
        # 测试5: 设置年龄 20-不限
        # ========================================
        logger.info("\n" + "=" * 80)
        logger.info("🧪 测试5: 设置年龄 20-不限")
        logger.info("=" * 80)

        result5 = await set_age_range_by_clicking(
            automation.page,
            recommend_frame,
            target_min=20,
            target_max=None  # 不限
        )

        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "click_track_05_range_20_unlimited.png"))

        # ========================================
        # 总结
        # ========================================
        logger.info("\n" + "=" * 80)
        logger.info("📋 测试总结")
        logger.info("=" * 80)

        all_results = [result1, result2, result3, result4, result5]

        successful_tests = sum(1 for r in all_results if r and r.get("success"))
        perfect_accuracy = sum(1 for r in all_results if r and r.get("accuracy") == "perfect")
        acceptable_accuracy = sum(1 for r in all_results if r and r.get("accuracy") == "acceptable")

        logger.info(f"\n测试总数: 5")
        logger.info(f"成功: {successful_tests}/5")
        logger.info(f"完全精确: {perfect_accuracy}")
        logger.info(f"可接受误差(±1岁): {acceptable_accuracy}")

        logger.info(f"\n详细结果:")
        logger.info(f"\n测试1 (单次点击25): {result1.get('success', False)}")
        if result1.get('success'):
            logger.info(f"  实际: {result1.get('actual')}, 误差: {result1.get('error', 'N/A')}")

        logger.info(f"\n测试2 (22-35): {result2.get('success', False)}")
        if result2.get('success'):
            logger.info(f"  实际: {result2['final_values']['min']}-{result2['final_values']['max']}")
            logger.info(f"  精度: {result2.get('accuracy', 'N/A')}")

        logger.info(f"\n测试3 (28-45): {result3.get('success', False)}")
        if result3.get('success'):
            logger.info(f"  实际: {result3['final_values']['min']}-{result3['final_values']['max']}")
            logger.info(f"  精度: {result3.get('accuracy', 'N/A')}")

        logger.info(f"\n测试4 (30-50): {result4.get('success', False)}")
        if result4.get('success'):
            logger.info(f"  实际: {result4['final_values']['min']}-{result4['final_values']['max']}")
            logger.info(f"  精度: {result4.get('accuracy', 'N/A')}")

        logger.info(f"\n测试5 (20-不限): {result5.get('success', False)}")
        if result5.get('success'):
            logger.info(f"  实际: {result5['final_values']['min']}-{result5['final_values']['max']}")
            logger.info(f"  精度: {result5.get('accuracy', 'N/A')}")

        logger.info("\n生成的截图:")
        logger.info("  click_track_00_initial.png - 初始状态")
        logger.info("  click_track_01_single_25.png - 测试1结果")
        logger.info("  click_track_02_range_22_35.png - 测试2结果")
        logger.info("  click_track_03_range_28_45.png - 测试3结果")
        logger.info("  click_track_04_range_30_50.png - 测试4结果")
        logger.info("  click_track_05_range_20_unlimited.png - 测试5结果")

        # 保持浏览器打开
        logger.info("\n⏳ 浏览器将保持打开 60 秒...")
        await asyncio.sleep(60)

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}", exc_info=True)

    finally:
        await automation.cleanup()


if __name__ == "__main__":
    asyncio.run(test_click_track_method())
