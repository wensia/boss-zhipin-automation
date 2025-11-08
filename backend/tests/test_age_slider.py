"""
深入测试年龄滑块组件
探索精准滑动调整年龄的各种方法

测试内容：
1. 分析滑块DOM结构
2. 测试拖拽滑块方法
3. 测试点击滑块轨道方法
4. 测试输入框直接输入方法
5. 测试JavaScript直接设置方法
6. 找出最精准可靠的实现方式
"""
import asyncio
import logging
import json
from pathlib import Path
from app.services.boss_automation import BossAutomation

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)


async def test_age_slider():
    """全面测试年龄滑块"""
    automation = BossAutomation()

    try:
        logger.info("=" * 80)
        logger.info("🎚️  开始测试年龄滑块组件")
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
        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "age_slider_01_initial.png"))

        # ========================================
        # 步骤1: 分析年龄滑块DOM结构
        # ========================================
        logger.info("\n" + "=" * 80)
        logger.info("📊 步骤1: 分析年龄滑块DOM结构")
        logger.info("=" * 80)

        # 使用JavaScript获取滑块详细信息
        slider_info = await recommend_frame.evaluate("""
        () => {
            // 查找年龄区块
            const ageSection = document.querySelector('.filter-item.age');
            if (!ageSection) {
                return { error: '未找到年龄区块' };
            }

            const result = {
                section_found: true,
                section_class: ageSection.className,
                section_html: ageSection.outerHTML.substring(0, 500),
                inputs: [],
                sliders: [],
                labels: []
            };

            // 查找输入框
            const inputs = ageSection.querySelectorAll('input');
            inputs.forEach((input, idx) => {
                result.inputs.push({
                    index: idx,
                    type: input.type,
                    value: input.value,
                    placeholder: input.placeholder || '',
                    className: input.className,
                    min: input.min || '',
                    max: input.max || '',
                    step: input.step || '',
                    readonly: input.readOnly,
                    disabled: input.disabled
                });
            });

            // 查找滑块组件
            const sliders = ageSection.querySelectorAll('.vue-slider, [class*="slider"]');
            sliders.forEach((slider, idx) => {
                result.sliders.push({
                    index: idx,
                    className: slider.className,
                    style: slider.style.cssText,
                    html: slider.outerHTML.substring(0, 300)
                });
            });

            // 查找滑块手柄
            const handles = ageSection.querySelectorAll('.vue-slider-dot, [class*="dot"]');
            result.handles = [];
            handles.forEach((handle, idx) => {
                const rect = handle.getBoundingClientRect();
                result.handles.push({
                    index: idx,
                    className: handle.className,
                    position_x: rect.left,
                    position_y: rect.top,
                    width: rect.width,
                    height: rect.height
                });
            });

            // 查找文本标签
            const labels = ageSection.querySelectorAll('.label, [class*="tooltip"]');
            labels.forEach((label, idx) => {
                result.labels.push({
                    index: idx,
                    text: label.textContent.trim(),
                    className: label.className
                });
            });

            return result;
        }
        """)

        # 保存分析结果
        analysis_file = SCREENSHOT_DIR / "age_slider_analysis.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(slider_info, f, ensure_ascii=False, indent=2)

        logger.info(f"📄 滑块结构分析已保存: {analysis_file}")

        if 'error' in slider_info:
            logger.error(f"❌ {slider_info['error']}")
            return

        # 打印关键信息
        logger.info(f"\n找到 {len(slider_info.get('inputs', []))} 个输入框")
        for inp in slider_info.get('inputs', []):
            logger.info(f"  输入框 {inp['index']}: type={inp['type']}, value={inp['value']}, "
                       f"readonly={inp['readonly']}, placeholder={inp['placeholder']}")

        logger.info(f"\n找到 {len(slider_info.get('sliders', []))} 个滑块组件")
        logger.info(f"找到 {len(slider_info.get('handles', []))} 个滑块手柄")
        for handle in slider_info.get('handles', []):
            logger.info(f"  手柄 {handle['index']}: 位置({handle['position_x']:.1f}, {handle['position_y']:.1f}), "
                       f"尺寸({handle['width']}x{handle['height']})")

        # ========================================
        # 步骤2: 测试方法1 - 直接输入数值到输入框
        # ========================================
        logger.info("\n" + "=" * 80)
        logger.info("🧪 步骤2: 方法1 - 输入框直接输入")
        logger.info("=" * 80)

        try:
            # 找到年龄区块
            age_section = await recommend_frame.query_selector('.filter-item.age')
            if age_section:
                # 查找所有输入框
                inputs = await age_section.query_selector_all('input')
                logger.info(f"找到 {len(inputs)} 个输入框")

                if len(inputs) >= 2:
                    # 第一个输入框 - 最小年龄
                    min_input = inputs[0]
                    logger.info("\n测试设置最小年龄为 25:")

                    # 方法1: 尝试直接填充
                    logger.info("  方法1a: 使用 fill()")
                    try:
                        await min_input.fill('')  # 先清空
                        await asyncio.sleep(0.3)
                        await min_input.fill('25')
                        await asyncio.sleep(1)

                        current_value = await min_input.get_attribute('value')
                        logger.info(f"    结果: value = {current_value}")

                        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "age_slider_02_fill_min.png"))
                    except Exception as e:
                        logger.error(f"    失败: {e}")

                    # 方法2: 尝试点击+输入
                    logger.info("  方法1b: 使用 click() + type()")
                    try:
                        await min_input.click(click_count=3)  # 三击全选
                        await asyncio.sleep(0.3)
                        await min_input.press('Backspace')
                        await asyncio.sleep(0.3)
                        await min_input.type('30', delay=100)
                        await asyncio.sleep(1)

                        current_value = await min_input.get_attribute('value')
                        logger.info(f"    结果: value = {current_value}")

                        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "age_slider_03_type_min.png"))
                    except Exception as e:
                        logger.error(f"    失败: {e}")

                    # 第二个输入框 - 最大年龄
                    if len(inputs) >= 2:
                        max_input = inputs[1]
                        logger.info("\n测试设置最大年龄为 35:")

                        try:
                            await max_input.click(click_count=3)
                            await asyncio.sleep(0.3)
                            await max_input.press('Backspace')
                            await asyncio.sleep(0.3)
                            await max_input.type('35', delay=100)
                            await asyncio.sleep(1)

                            current_value = await max_input.get_attribute('value')
                            logger.info(f"    结果: value = {current_value}")

                            await automation.page.screenshot(path=str(SCREENSHOT_DIR / "age_slider_04_type_max.png"))
                        except Exception as e:
                            logger.error(f"    失败: {e}")

        except Exception as e:
            logger.error(f"❌ 输入框测试失败: {e}", exc_info=True)

        # ========================================
        # 步骤3: 测试方法2 - JavaScript直接设置
        # ========================================
        logger.info("\n" + "=" * 80)
        logger.info("🧪 步骤3: 方法2 - JavaScript直接设置")
        logger.info("=" * 80)

        try:
            result = await recommend_frame.evaluate("""
            (values) => {
                const ageSection = document.querySelector('.filter-item.age');
                if (!ageSection) return { success: false, message: '未找到年龄区块' };

                const inputs = ageSection.querySelectorAll('input');
                if (inputs.length < 2) return { success: false, message: '输入框数量不足' };

                const [minInput, maxInput] = inputs;

                // 设置值
                minInput.value = values.min;
                maxInput.value = values.max;

                // 触发change事件
                minInput.dispatchEvent(new Event('input', { bubbles: true }));
                minInput.dispatchEvent(new Event('change', { bubbles: true }));
                maxInput.dispatchEvent(new Event('input', { bubbles: true }));
                maxInput.dispatchEvent(new Event('change', { bubbles: true }));

                return {
                    success: true,
                    min_value: minInput.value,
                    max_value: maxInput.value
                };
            }
            """, {"min": "22", "max": "40"})

            logger.info(f"JavaScript设置结果: {json.dumps(result, ensure_ascii=False)}")
            await asyncio.sleep(1)
            await automation.page.screenshot(path=str(SCREENSHOT_DIR / "age_slider_05_js_set.png"))

        except Exception as e:
            logger.error(f"❌ JavaScript设置失败: {e}", exc_info=True)

        # ========================================
        # 步骤4: 测试方法3 - 拖拽滑块手柄
        # ========================================
        logger.info("\n" + "=" * 80)
        logger.info("🧪 步骤4: 方法3 - 拖拽滑块手柄")
        logger.info("=" * 80)

        try:
            # 查找滑块手柄
            handles = await recommend_frame.query_selector_all('.vue-slider-dot')
            logger.info(f"找到 {len(handles)} 个滑块手柄")

            if len(handles) >= 1:
                # 测试拖拽第一个手柄（最小年龄）
                logger.info("\n测试拖拽最小年龄手柄:")
                min_handle = handles[0]

                # 获取手柄位置
                box = await min_handle.bounding_box()
                if box:
                    logger.info(f"  手柄位置: x={box['x']:.1f}, y={box['y']:.1f}, "
                              f"w={box['width']:.1f}, h={box['height']:.1f}")

                    # 计算中心点
                    start_x = box['x'] + box['width'] / 2
                    start_y = box['y'] + box['height'] / 2

                    # 尝试向右拖动50像素
                    logger.info(f"  从 ({start_x:.1f}, {start_y:.1f}) 向右拖动 50 像素")

                    await automation.page.mouse.move(start_x, start_y)
                    await asyncio.sleep(0.3)
                    await automation.page.mouse.down()
                    await asyncio.sleep(0.2)
                    await automation.page.mouse.move(start_x + 50, start_y, steps=10)
                    await asyncio.sleep(0.3)
                    await automation.page.mouse.up()
                    await asyncio.sleep(1)

                    logger.info("  拖拽完成")
                    await automation.page.screenshot(path=str(SCREENSHOT_DIR / "age_slider_06_drag_min.png"))

            if len(handles) >= 2:
                # 测试拖拽第二个手柄（最大年龄）
                logger.info("\n测试拖拽最大年龄手柄:")
                max_handle = handles[1]

                box = await max_handle.bounding_box()
                if box:
                    logger.info(f"  手柄位置: x={box['x']:.1f}, y={box['y']:.1f}")

                    start_x = box['x'] + box['width'] / 2
                    start_y = box['y'] + box['height'] / 2

                    # 向左拖动30像素
                    logger.info(f"  从 ({start_x:.1f}, {start_y:.1f}) 向左拖动 30 像素")

                    await automation.page.mouse.move(start_x, start_y)
                    await asyncio.sleep(0.3)
                    await automation.page.mouse.down()
                    await asyncio.sleep(0.2)
                    await automation.page.mouse.move(start_x - 30, start_y, steps=10)
                    await asyncio.sleep(0.3)
                    await automation.page.mouse.up()
                    await asyncio.sleep(1)

                    logger.info("  拖拽完成")
                    await automation.page.screenshot(path=str(SCREENSHOT_DIR / "age_slider_07_drag_max.png"))

        except Exception as e:
            logger.error(f"❌ 拖拽测试失败: {e}", exc_info=True)

        # ========================================
        # 步骤5: 测试方法4 - 点击滑块轨道
        # ========================================
        logger.info("\n" + "=" * 80)
        logger.info("🧪 步骤5: 方法4 - 点击滑块轨道")
        logger.info("=" * 80)

        try:
            # 查找滑块轨道
            slider_track = await recommend_frame.query_selector('.vue-slider')
            if slider_track:
                box = await slider_track.bounding_box()
                if box:
                    logger.info(f"滑块轨道: x={box['x']:.1f}, y={box['y']:.1f}, w={box['width']:.1f}")

                    # 点击轨道的1/4位置（设置较小年龄）
                    click_x = box['x'] + box['width'] * 0.25
                    click_y = box['y'] + box['height'] / 2

                    logger.info(f"  点击轨道 1/4 位置: ({click_x:.1f}, {click_y:.1f})")
                    await automation.page.mouse.click(click_x, click_y)
                    await asyncio.sleep(1)

                    await automation.page.screenshot(path=str(SCREENSHOT_DIR / "age_slider_08_click_track.png"))

        except Exception as e:
            logger.error(f"❌ 点击轨道测试失败: {e}", exc_info=True)

        # ========================================
        # 步骤6: 读取最终值
        # ========================================
        logger.info("\n" + "=" * 80)
        logger.info("📊 步骤6: 读取当前年龄值")
        logger.info("=" * 80)

        final_values = await recommend_frame.evaluate("""
        () => {
            const ageSection = document.querySelector('.filter-item.age');
            if (!ageSection) return null;

            const inputs = ageSection.querySelectorAll('input');
            const tooltips = ageSection.querySelectorAll('.vue-slider-dot-tooltip-text');

            return {
                input_values: Array.from(inputs).map(inp => inp.value),
                tooltip_texts: Array.from(tooltips).map(tt => tt.textContent.trim())
            };
        }
        """)

        logger.info(f"\n最终年龄值:")
        logger.info(f"  输入框: {final_values.get('input_values', [])}")
        logger.info(f"  提示文本: {final_values.get('tooltip_texts', [])}")

        # 最终截图
        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "age_slider_09_final.png"))

        # ========================================
        # 总结
        # ========================================
        logger.info("\n" + "=" * 80)
        logger.info("📋 测试总结")
        logger.info("=" * 80)
        logger.info("✅ 已完成年龄滑块所有测试方法")
        logger.info("\n生成的截图:")
        logger.info("  01_initial.png - 初始状态")
        logger.info("  02_fill_min.png - fill()方法设置最小年龄")
        logger.info("  03_type_min.png - type()方法设置最小年龄")
        logger.info("  04_type_max.png - type()方法设置最大年龄")
        logger.info("  05_js_set.png - JavaScript直接设置")
        logger.info("  06_drag_min.png - 拖拽最小年龄手柄")
        logger.info("  07_drag_max.png - 拖拽最大年龄手柄")
        logger.info("  08_click_track.png - 点击滑块轨道")
        logger.info("  09_final.png - 最终状态")
        logger.info(f"\n分析数据: {analysis_file}")

        # 保持浏览器打开
        logger.info("\n⏳ 浏览器将保持打开 60 秒...")
        await asyncio.sleep(60)

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}", exc_info=True)

    finally:
        await automation.cleanup()


if __name__ == "__main__":
    asyncio.run(test_age_slider())
