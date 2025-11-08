"""
检查页面中的 iframe - 职位选择器可能在 iframe 中
"""
import asyncio
import logging
from pathlib import Path
from app.services.boss_automation import BossAutomation

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)


async def check_iframes():
    """检查页面中的 iframe"""
    automation = BossAutomation()

    try:
        logger.info("=" * 80)
        logger.info("🔍 检查页面中的 iframe")
        logger.info("=" * 80)

        # 初始化
        await automation.initialize(headless=False)
        await asyncio.sleep(2)

        # 登录检查
        login_status = await automation.check_login_status()
        if not login_status.get('logged_in'):
            logger.error("❌ 未登录")
            return

        # 导航到推荐页面
        logger.info("\n📍 导航到推荐页面...")
        await automation.navigate_to_recommend_page()

        # 等待页面加载
        logger.info("⏳ 等待15秒让页面完全加载...")
        await asyncio.sleep(15)

        # 截图
        await automation.page.screenshot(path=str(SCREENSHOT_DIR / "iframe_check_01.png"))
        logger.info("📸 已保存截图")

        # 方法1: 检查主页面中的 iframe
        logger.info("\n" + "=" * 80)
        logger.info("📊 检查主页面中的 iframe 元素")
        logger.info("=" * 80)

        iframe_info = await automation.page.evaluate("""
            () => {
                const iframes = document.querySelectorAll('iframe');
                const info = [];

                iframes.forEach((iframe, idx) => {
                    const rect = iframe.getBoundingClientRect();
                    info.push({
                        index: idx,
                        id: iframe.id || '',
                        name: iframe.name || '',
                        src: iframe.src || '',
                        className: iframe.className || '',
                        width: Math.round(rect.width),
                        height: Math.round(rect.height),
                        visible: rect.width > 0 && rect.height > 0,
                        position: {
                            top: Math.round(rect.top),
                            left: Math.round(rect.left)
                        }
                    });
                });

                return info;
            }
        """)

        logger.info(f"\n找到 {len(iframe_info)} 个 iframe:")
        for info in iframe_info:
            logger.info(f"\niframe {info['index']}:")
            logger.info(f"  ID: {info['id']}")
            logger.info(f"  name: {info['name']}")
            logger.info(f"  src: {info['src']}")
            logger.info(f"  className: {info['className']}")
            logger.info(f"  尺寸: {info['width']}x{info['height']}")
            logger.info(f"  可见: {info['visible']}")
            logger.info(f"  位置: top={info['position']['top']}, left={info['position']['left']}")

        # 方法2: 使用 Playwright 获取所有 frame
        logger.info("\n" + "=" * 80)
        logger.info("📊 使用 Playwright 获取所有 frame")
        logger.info("=" * 80)

        frames = automation.page.frames
        logger.info(f"\n找到 {len(frames)} 个 frame (包括主 frame):")

        for idx, frame in enumerate(frames):
            logger.info(f"\nFrame {idx}:")
            logger.info(f"  name: {frame.name}")
            logger.info(f"  url: {frame.url}")
            logger.info(f"  是主frame: {frame == automation.page.main_frame}")

        # 方法3: 在每个 frame 中查找职位选择器
        logger.info("\n" + "=" * 80)
        logger.info("🔍 在每个 frame 中查找职位选择器")
        logger.info("=" * 80)

        for idx, frame in enumerate(frames):
            logger.info(f"\n检查 Frame {idx} ({frame.name or 'unnamed'}):")
            logger.info(f"  URL: {frame.url}")

            try:
                # 在这个 frame 中查找包含职位信息的元素
                job_elements = await frame.evaluate("""
                    () => {
                        const elements = [];
                        const allElems = document.querySelectorAll('*');

                        allElems.forEach(elem => {
                            const text = elem.textContent ? elem.textContent.trim() : '';
                            const rect = elem.getBoundingClientRect();

                            // 查找包含薪资格式或职位关键词的元素
                            if (text.includes('K') || text.includes('新媒体') || text.includes('天津')) {
                                if (rect.width > 100 && rect.height > 15 && text.length < 300) {
                                    elements.push({
                                        tagName: elem.tagName,
                                        className: typeof elem.className === 'string' ? elem.className : '',
                                        id: elem.id || '',
                                        text: text.substring(0, 150),
                                        position: {
                                            top: Math.round(rect.top),
                                            left: Math.round(rect.left),
                                            width: Math.round(rect.width),
                                            height: Math.round(rect.height)
                                        }
                                    });
                                }
                            }
                        });

                        return elements.slice(0, 20); // 返回前20个
                    }
                """)

                logger.info(f"  找到 {len(job_elements)} 个可能的职位元素:")
                for elem_idx, elem in enumerate(job_elements[:10], 1):
                    logger.info(f"\n    元素 {elem_idx}:")
                    logger.info(f"      标签: {elem['tagName']}")
                    logger.info(f"      类名: {elem['className']}")
                    logger.info(f"      ID: {elem['id']}")
                    logger.info(f"      位置: top={elem['position']['top']}, left={elem['position']['left']}, width={elem['position']['width']}")
                    logger.info(f"      文本: {elem['text']}")

            except Exception as e:
                logger.warning(f"  ⚠️ 检查 frame 失败: {e}")

        # 方法4: 特别检查包含职位信息的 frame
        logger.info("\n" + "=" * 80)
        logger.info("🎯 尝试在 frame 中直接查找职位选择器")
        logger.info("=" * 80)

        for idx, frame in enumerate(frames):
            logger.info(f"\nFrame {idx}:")

            try:
                # 尝试使用 text 选择器
                elements = await frame.query_selector_all("text=/\\d+-\\d+K/")
                if elements:
                    logger.info(f"  ✅ 找到 {len(elements)} 个包含薪资格式的元素!")

                    for elem_idx, elem in enumerate(elements[:5], 1):
                        text = await elem.text_content()
                        html = await elem.evaluate("el => el.outerHTML")
                        logger.info(f"\n  元素 {elem_idx}:")
                        logger.info(f"    文本: {text}")
                        logger.info(f"    HTML: {html[:300]}")

                        # 如果找到职位选择器，尝试点击
                        if '天津' in text and 'K' in text:
                            logger.info(f"\n  🎯 找到职位选择器！尝试点击...")

                            # 截图点击前
                            await automation.page.screenshot(path=str(SCREENSHOT_DIR / "iframe_check_02_before_click.png"))

                            await elem.click()
                            await asyncio.sleep(2)

                            # 截图点击后
                            await automation.page.screenshot(path=str(SCREENSHOT_DIR / "iframe_check_03_after_click.png"))
                            logger.info(f"  📸 已保存点击前后截图")

                            # 查找下拉列表
                            logger.info(f"\n  🔍 查找下拉列表...")
                            dropdown_lis = await frame.query_selector_all("ul li")
                            logger.info(f"  找到 {len(dropdown_lis)} 个 li 元素")

                            for li_idx, li in enumerate(dropdown_lis[:10], 1):
                                value = await li.get_attribute("value")
                                li_text = await li.text_content()
                                logger.info(f"\n    li {li_idx}:")
                                logger.info(f"      value: {value}")
                                logger.info(f"      文本: {li_text[:150]}")

                            break  # 找到并点击后退出循环
                else:
                    logger.info(f"  未找到薪资格式元素")

            except Exception as e:
                logger.warning(f"  ⚠️ 查找失败: {e}")

        logger.info("\n⏳ 浏览器将保持打开 120 秒...")
        await asyncio.sleep(120)

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}", exc_info=True)

    finally:
        await automation.cleanup()


if __name__ == "__main__":
    asyncio.run(check_iframes())
