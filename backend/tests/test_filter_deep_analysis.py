"""
深入分析筛选弹窗的DOM结构
获取所有筛选组件的选择器、属性和交互方式
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


async def analyze_filter_structure():
    """深入分析筛选弹窗结构"""
    automation = BossAutomation()

    try:
        logger.info("=" * 80)
        logger.info("🔬 深入分析筛选弹窗DOM结构")
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

        # 找到 iframe
        recommend_frame = None
        for frame in automation.page.frames:
            if frame.name == 'recommendFrame':
                recommend_frame = frame
                break

        if not recommend_frame:
            logger.error("❌ 未找到 recommendFrame iframe")
            return

        logger.info("✅ 找到 recommendFrame")

        # 点击筛选按钮
        filter_button_selector = "#headerWrap > div > div > div.fl.recommend-filter.op-filter > div > div"
        filter_button = await recommend_frame.wait_for_selector(filter_button_selector, timeout=10000)
        await filter_button.click()
        await asyncio.sleep(2)

        logger.info("✅ 筛选弹窗已打开")

        # 使用JavaScript获取筛选弹窗的完整DOM结构
        logger.info("\n" + "=" * 80)
        logger.info("📊 分析筛选弹窗DOM结构")
        logger.info("=" * 80)

        # 执行JavaScript来获取所有筛选项的详细信息
        filter_data = await recommend_frame.evaluate("""
        () => {
            const result = {
                sections: []
            };

            // 查找筛选弹窗容器
            const dialog = document.querySelector('.filter-dialog-content') ||
                          document.querySelector('[class*="filter"]') ||
                          document.querySelector('.dialog-wrap');

            if (!dialog) {
                return { error: '未找到筛选弹窗容器' };
            }

            // 获取所有筛选区块
            const sections = dialog.querySelectorAll('.filter-item, [class*="filter-item"]');

            sections.forEach((section, index) => {
                const sectionData = {
                    index: index,
                    className: section.className,
                    label: '',
                    type: '',
                    options: []
                };

                // 获取标签
                const label = section.querySelector('.label, [class*="label"]');
                if (label) {
                    sectionData.label = label.textContent.trim();
                }

                // 查找按钮类型的选项
                const buttons = section.querySelectorAll('button, [role="button"], .btn, [class*="btn"]');
                buttons.forEach(btn => {
                    const text = btn.textContent.trim();
                    const className = btn.className;
                    const isSelected = className.includes('selected') || className.includes('active');

                    if (text) {
                        sectionData.options.push({
                            type: 'button',
                            text: text,
                            className: className,
                            selected: isSelected
                        });
                    }
                });

                // 查找输入框
                const inputs = section.querySelectorAll('input');
                inputs.forEach(input => {
                    sectionData.options.push({
                        type: input.type,
                        value: input.value,
                        placeholder: input.placeholder || '',
                        className: input.className
                    });
                });

                if (sectionData.label || sectionData.options.length > 0) {
                    result.sections.push(sectionData);
                }
            });

            return result;
        }
        """)

        # 保存分析结果
        analysis_file = SCREENSHOT_DIR / "filter_structure_analysis.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(filter_data, f, ensure_ascii=False, indent=2)

        logger.info(f"📄 DOM结构分析已保存: {analysis_file}")

        # 打印分析结果
        if 'error' in filter_data:
            logger.error(f"❌ {filter_data['error']}")
        else:
            logger.info(f"\n找到 {len(filter_data.get('sections', []))} 个筛选区块:")
            for section in filter_data.get('sections', []):
                logger.info(f"\n区块 {section['index']}: {section['label']}")
                logger.info(f"  类名: {section['className']}")
                logger.info(f"  选项数量: {len(section['options'])}")

                # 显示前5个选项
                for i, opt in enumerate(section['options'][:5]):
                    if opt['type'] == 'button':
                        logger.info(f"    [{i}] {opt['text']} (选中: {opt['selected']})")
                    else:
                        logger.info(f"    [{i}] {opt['type']}: {opt.get('value', opt.get('placeholder', ''))}")

        # 获取更详细的选择器信息
        logger.info("\n" + "=" * 80)
        logger.info("🔍 获取具体选择器信息")
        logger.info("=" * 80)

        # 测试各类选择器
        selector_tests = [
            ("年龄输入框", "input[type='number']"),
            ("不限按钮", "text=不限"),
            ("活跃度区块", "[class*='activity'], [class*='active']"),
            ("性别选项", "text=男"),
            ("学历要求", "text=本科"),
            ("经验要求", "text=1-3年"),
            ("确定按钮", "text=确定"),
            ("取消按钮", "text=取消"),
        ]

        selector_results = {}
        for name, selector in selector_tests:
            try:
                elements = await recommend_frame.query_selector_all(selector)
                count = len(elements)
                selector_results[name] = {
                    'selector': selector,
                    'count': count,
                    'found': count > 0
                }
                logger.info(f"  {name}: {selector} - 找到 {count} 个")

                # 如果找到元素，获取第一个的详细信息
                if count > 0:
                    first_element = elements[0]
                    tag_name = await first_element.evaluate('el => el.tagName')
                    class_name = await first_element.get_attribute('class') or ''
                    logger.info(f"    标签: {tag_name}, 类名: {class_name}")
            except Exception as e:
                selector_results[name] = {
                    'selector': selector,
                    'error': str(e)
                }
                logger.error(f"  {name}: 失败 - {e}")

        # 保存选择器测试结果
        selector_file = SCREENSHOT_DIR / "filter_selectors.json"
        with open(selector_file, 'w', encoding='utf-8') as f:
            json.dump(selector_results, f, ensure_ascii=False, indent=2)

        logger.info(f"\n📄 选择器测试结果已保存: {selector_file}")

        # 测试通过类名查找所有"不限"按钮
        logger.info("\n" + "=" * 80)
        logger.info("🧪 测试查找所有筛选区块")
        logger.info("=" * 80)

        filter_rows = await recommend_frame.query_selector_all(".filter-item, [class*='filter-row']")
        logger.info(f"找到 {len(filter_rows)} 个筛选行")

        for i, row in enumerate(filter_rows[:10]):  # 只显示前10个
            try:
                text = await row.text_content()
                class_name = await row.get_attribute('class')
                logger.info(f"\n行 {i}:")
                logger.info(f"  类名: {class_name}")
                logger.info(f"  文本: {text[:100] if text else '无'}...")  # 只显示前100字符
            except:
                pass

        # 截图保存
        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "filter_analysis_complete.png"))

        logger.info("\n" + "=" * 80)
        logger.info("✅ 分析完成")
        logger.info("=" * 80)
        logger.info(f"📊 DOM结构: {analysis_file}")
        logger.info(f"🔍 选择器结果: {selector_file}")
        logger.info(f"📸 截图: filter_analysis_complete.png")

        # 保持浏览器打开
        logger.info("\n⏳ 浏览器将保持打开 60 秒...")
        await asyncio.sleep(60)

    except Exception as e:
        logger.error(f"❌ 分析失败: {e}", exc_info=True)

    finally:
        await automation.cleanup()


if __name__ == "__main__":
    asyncio.run(analyze_filter_structure())
